from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
import hashlib
import math
from typing import Sequence

from sentence_transformers import SentenceTransformer

from backend.app.analysis.esco_mapper import ESCOMapResult, ESCOMapStatus
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence
from backend.app.domain.matching import (
    MatchRelationship,
    MatchingResult,
    SkillMatch,
)
from backend.app.domain.skill import Skill


class MatchingStrategy(StrEnum):
    """Supported Phase 5 skill-matching strategies."""

    KEYWORD = "keyword"
    TAXONOMY = "taxonomy"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class MatchingThresholds:
    """Configurable heuristic thresholds for semantic matching."""

    strong_semantic: float = 0.80
    partial: float = 0.65
    related: float = 0.50

    def __post_init__(self) -> None:
        values = (
            self.strong_semantic,
            self.partial,
            self.related,
        )
        if any(not 0.0 <= value <= 1.0 for value in values):
            raise ValueError("Matching thresholds must be between 0.0 and 1.0.")
        if not (
            self.strong_semantic
            > self.partial
            > self.related
        ):
            raise ValueError(
                "Thresholds must satisfy "
                "strong_semantic > partial > related."
            )


@dataclass(frozen=True)
class SemanticModelConfig:
    """Explicit semantic encoder configuration."""

    model_name: str = "all-MiniLM-L6-v2"


@dataclass(frozen=True)
class _Candidate:
    resume_skill: Skill
    job_skill: Skill
    similarity: float
    relationship: MatchRelationship
    method: str


class SkillMatcher:
    """Match resume skills against job-description skills.

    Phase 5 responsibilities are limited to skill-level relationships,
    similarity, evidence, and confidence. This component does not calculate
    candidate-job scores, rankings, explanations, or recommendations.
    """

    ENGINE_VERSION = "phase5-skill-matcher-v1"

    def __init__(
        self,
        *,
        strategy: MatchingStrategy = MatchingStrategy.HYBRID,
        thresholds: MatchingThresholds | None = None,
        semantic_model: SemanticModelConfig | None = None,
    ) -> None:
        self.strategy = strategy
        self.thresholds = thresholds or MatchingThresholds()
        self.semantic_model = semantic_model or SemanticModelConfig()

    def match(
        self,
        resume_skills: Sequence[Skill],
        job_skills: Sequence[Skill],
        *,
        resume_esco: Sequence[ESCOMapResult] | None = None,
        job_esco: Sequence[ESCOMapResult] | None = None,
    ) -> MatchingResult:
        """Match resume skills against JD skills."""

        resume = tuple(resume_skills)
        job = tuple(job_skills)

        if not resume or not job:
            return MatchingResult(
                skill_matches=[],
                metadata={
                    "engine_version": self.ENGINE_VERSION,
                    "strategy": self.strategy.value,
                    "candidate_count": len(resume),
                    "job_skill_count": len(job),
                },
            )

        resume_taxonomy = self._align_esco_results(
            resume,
            tuple(resume_esco or ()),
        )
        job_taxonomy = self._align_esco_results(
            job,
            tuple(job_esco or ()),
        )

        candidates: list[_Candidate] = []

        for resume_skill in resume:
            best: _Candidate | None = None

            for job_skill in job:
                candidate = self._match_pair(
                    resume_skill,
                    job_skill,
                    resume_taxonomy.get(resume_skill.skill_id),
                    job_taxonomy.get(job_skill.skill_id),
                )

                if candidate is None:
                    continue

                if best is None or (
                    candidate.similarity,
                    candidate.relationship.value,
                ) > (
                    best.similarity,
                    best.relationship.value,
                ):
                    best = candidate

            if best is not None:
                candidates.append(best)

        matches = [
            self._to_skill_match(candidate)
            for candidate in candidates
        ]

        return MatchingResult(
            skill_matches=matches,
            metadata={
                "engine_version": self.ENGINE_VERSION,
                "strategy": self.strategy.value,
                "thresholds": {
                    "strong_semantic": self.thresholds.strong_semantic,
                    "partial": self.thresholds.partial,
                    "related": self.thresholds.related,
                },
                "semantic_model": self.semantic_model.model_name,
                "candidate_count": len(resume),
                "job_skill_count": len(job),
                "match_count": len(matches),
            },
        )

    def _match_pair(
        self,
        resume_skill: Skill,
        job_skill: Skill,
        resume_esco: ESCOMapResult | None,
        job_esco: ESCOMapResult | None,
    ) -> _Candidate | None:
        resume_name = resume_skill.canonical_name.strip().lower()
        job_name = job_skill.canonical_name.strip().lower()

        if resume_name == job_name:
            return _Candidate(
                resume_skill=resume_skill,
                job_skill=job_skill,
                similarity=1.0,
                relationship=MatchRelationship.EXACT,
                method="canonical_exact",
            )

        if self.strategy == MatchingStrategy.KEYWORD:
            return None

        if self.strategy == MatchingStrategy.TAXONOMY:
            return self._taxonomy_candidate(
                resume_skill,
                job_skill,
                resume_esco,
                job_esco,
            )

        semantic_candidate = self._semantic_candidate(
            resume_skill,
            job_skill,
        )

        if self.strategy == MatchingStrategy.SEMANTIC:
            return semantic_candidate

        taxonomy_candidate = self._taxonomy_candidate(
            resume_skill,
            job_skill,
            resume_esco,
            job_esco,
        )

        if taxonomy_candidate is None:
            return semantic_candidate

        if semantic_candidate is None:
            return taxonomy_candidate

        if taxonomy_candidate.similarity >= semantic_candidate.similarity:
            return taxonomy_candidate

        return semantic_candidate

    def _taxonomy_candidate(
        self,
        resume_skill: Skill,
        job_skill: Skill,
        resume_esco: ESCOMapResult | None,
        job_esco: ESCOMapResult | None,
    ) -> _Candidate | None:
        if resume_esco is None or job_esco is None:
            return None

        if (
            resume_esco.status != ESCOMapStatus.MAPPED
            or job_esco.status != ESCOMapStatus.MAPPED
        ):
            return None

        resume_uris = {
            candidate.uri
            for candidate in resume_esco.candidates
            if candidate.uri
        }
        job_uris = {
            candidate.uri
            for candidate in job_esco.candidates
            if candidate.uri
        }

        if not resume_uris or not job_uris:
            return None

        if resume_uris.isdisjoint(job_uris):
            return None

        shared_uris = resume_uris.intersection(job_uris)

        resume_confidence = max(
            (
                candidate.confidence
                for candidate in resume_esco.candidates
                if candidate.uri in shared_uris
            ),
            default=0.0,
        )
        job_confidence = max(
            (
                candidate.confidence
                for candidate in job_esco.candidates
                if candidate.uri in shared_uris
            ),
            default=0.0,
        )
        confidence = min(resume_confidence, job_confidence)

        return _Candidate(
            resume_skill=resume_skill,
            job_skill=job_skill,
            similarity=confidence,
            relationship=MatchRelationship.STRONG_SEMANTIC,
            method="esco_taxonomy",
        )

    def _semantic_candidate(
        self,
        resume_skill: Skill,
        job_skill: Skill,
    ) -> _Candidate | None:
        similarity = self._cosine_similarity(
            resume_skill.canonical_name,
            job_skill.canonical_name,
        )

        if similarity >= self.thresholds.strong_semantic:
            relationship = MatchRelationship.STRONG_SEMANTIC
        elif similarity >= self.thresholds.partial:
            relationship = MatchRelationship.PARTIAL
        elif similarity >= self.thresholds.related:
            relationship = MatchRelationship.RELATED
        else:
            relationship = MatchRelationship.UNMATCHED

        return _Candidate(
            resume_skill=resume_skill,
            job_skill=job_skill,
            similarity=similarity,
            relationship=relationship,
            method="semantic_cosine",
        )

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_encoder(model_name: str) -> SentenceTransformer:
        """Load the semantic model once per process/model name."""
        return SentenceTransformer(model_name)

    def _cosine_similarity(
        self,
        resume_name: str,
        job_name: str,
    ) -> float:
        encoder = self._get_encoder(self.semantic_model.model_name)
        embeddings = encoder.encode(
            [resume_name, job_name],
            normalize_embeddings=True,
        )

        similarity = float(
            sum(
                left * right
                for left, right in zip(
                    embeddings[0],
                    embeddings[1],
                    strict=True,
                )
            )
        )

        # Protect the domain contract against tiny floating-point drift.
        return max(0.0, min(1.0, similarity))

    @staticmethod
    def _align_esco_results(
        skills: Sequence[Skill],
        results: Sequence[ESCOMapResult],
    ) -> dict[str, ESCOMapResult]:
        """Align ESCO results to skills using canonical names."""

        by_name = {
            result.canonical_name: result
            for result in results
        }

        return {
            skill.skill_id: by_name[skill.canonical_name]
            for skill in skills
            if skill.canonical_name in by_name
        }

    @staticmethod
    def _to_skill_match(candidate: _Candidate) -> SkillMatch:
        evidence = [
            *candidate.resume_skill.evidence,
            *candidate.job_skill.evidence,
        ]

        confidence = SkillMatcher._build_confidence(
            candidate,
        )

        return SkillMatch(
            resume_skill_id=candidate.resume_skill.skill_id,
            job_skill_id=candidate.job_skill.skill_id,
            relationship=candidate.relationship,
            similarity=candidate.similarity,
            confidence=confidence,
            evidence=evidence,
            rationale=candidate.method,
        )

    @staticmethod
    def _build_confidence(candidate: _Candidate) -> Confidence:
        skill_scores = [
            score
            for score in (
                candidate.resume_skill.confidence.score
                if candidate.resume_skill.confidence
                else None,
                candidate.job_skill.confidence.score
                if candidate.job_skill.confidence
                else None,
            )
            if score is not None
        ]

        base = min(skill_scores) if skill_scores else candidate.similarity

        method_factor = {
            "canonical_exact": 1.0,
            "esco_taxonomy": 0.95,
            "semantic_cosine": 0.90,
        }.get(candidate.method, 0.80)

        score = max(0.0, min(1.0, base * method_factor))

        if score >= 0.85:
            level = ConfidenceLevel.HIGH
        elif score >= 0.65:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        return Confidence(
            score=score,
            level=level,
            components={
                "skill_confidence": base,
                "method_factor": method_factor,
                "similarity": candidate.similarity,
            },
            rationale=f"derived_from_{candidate.method}",
        )
