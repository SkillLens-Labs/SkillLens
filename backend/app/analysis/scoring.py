from __future__ import annotations

from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.job import JobProfile
from backend.app.domain.matching import (
    JobRequirement,
    JobRequirementCategory,
    JobRequirementType,
    MatchingResult,
    RequirementAlignment,
    RequirementMatchStatus,
    SkillMatch,
)
from backend.app.domain.scoring import (
    DimensionScore,
    ScoreContribution,
    ScoringResult,
)


class ScoringAnalyzer:
    """Deterministic, evidence-aware resume-to-JD scoring."""

    ENGINE_VERSION = "phase6-scoring-v1"

    _WEIGHTS = {
        "required_skills": 0.50,
        "preferred_skills": 0.15,
        "experience": 0.15,
        "education": 0.10,
        "domain": 0.10,
    }

    _ALIGNMENT_VALUES = {
        RequirementMatchStatus.MATCHED: 1.0,
        RequirementMatchStatus.PARTIAL: 0.5,
        RequirementMatchStatus.UNMATCHED: 0.0,
    }

    def score(
        self,
        *,
        job_profile: JobProfile,
        requirements: list[JobRequirement],
        matching: MatchingResult,
        resume_skills: list,
        job_skills: list,
    ) -> ScoringResult:
        alignments = {
            alignment.requirement_id: alignment
            for alignment in matching.requirement_alignments
        }

        contributions: list[ScoreContribution] = []

        required_score, required_available = self._score_requirement_dimension(
            requirements=requirements,
            alignments=alignments,
            requirement_type=JobRequirementType.REQUIRED,
            categories={JobRequirementCategory.SKILL},
            dimension="required_skills",
            contributions=contributions,
        )

        preferred_score, preferred_available = self._score_requirement_dimension(
            requirements=requirements,
            alignments=alignments,
            requirement_type=JobRequirementType.PREFERRED,
            categories={JobRequirementCategory.SKILL},
            dimension="preferred_skills",
            contributions=contributions,
        )

        experience_score, experience_available = self._score_requirement_dimension(
            requirements=requirements,
            alignments=alignments,
            requirement_type=None,
            categories={JobRequirementCategory.EXPERIENCE},
            dimension="experience",
            contributions=contributions,
        )

        education_score, education_available = self._score_requirement_dimension(
            requirements=requirements,
            alignments=alignments,
            requirement_type=None,
            categories={JobRequirementCategory.EDUCATION},
            dimension="education",
            contributions=contributions,
        )

        domain_score, domain_available = self._score_domain(
            job_profile=job_profile,
            job_skills=job_skills,
            matching=matching,
            contributions=contributions,
        )

        skill_score = self._weighted_skill_score(
            required_score=required_score,
            required_available=required_available,
            preferred_score=preferred_score,
            preferred_available=preferred_available,
        )

        dimension_values = {
            "required_skills": (required_score, required_available),
            "preferred_skills": (preferred_score, preferred_available),
            "experience": (experience_score, experience_available),
            "education": (education_score, education_available),
            "domain": (domain_score, domain_available),
        }

        available_weight = sum(
            self._WEIGHTS[name]
            for name, (_, available) in dimension_values.items()
            if available
        )

        if available_weight:
            overall_normalized = sum(
                score * self._WEIGHTS[name]
                for name, (score, available) in dimension_values.items()
                if available
            ) / available_weight
        else:
            overall_normalized = 0.0

        dimension_scores = [
            DimensionScore(
                dimension=name,
                score=round(score * 100.0, 2),
                weight=self._WEIGHTS[name],
            )
            for name, (score, available) in dimension_values.items()
            if available
        ]

        confidence = self._build_confidence(
            requirements=requirements,
            matching=matching,
            available_dimensions=sum(
                available for _, available in dimension_values.values()
            ),
        )

        return ScoringResult(
            overall_score=round(overall_normalized * 100.0, 2),
            skill_score=round(skill_score * 100.0, 2),
            required_skill_score=round(required_score * 100.0, 2),
            preferred_skill_score=round(preferred_score * 100.0, 2),
            experience_score=round(experience_score * 100.0, 2),
            education_score=round(education_score * 100.0, 2),
            domain_score=round(domain_score * 100.0, 2),
            dimension_scores=dimension_scores,
            weights=dict(self._WEIGHTS),
            contributions=contributions,
            penalties=[],
            bonuses=[],
            confidence=confidence,
        )

    def _score_requirement_dimension(
        self,
        *,
        requirements: list[JobRequirement],
        alignments: dict[str, RequirementAlignment],
        requirement_type: JobRequirementType | None,
        categories: set[JobRequirementCategory],
        dimension: str,
        contributions: list[ScoreContribution],
    ) -> tuple[float, bool]:
        selected = [
            requirement
            for requirement in requirements
            if requirement.category in categories
            and (
                requirement_type is None
                or requirement.requirement_type == requirement_type
            )
        ]

        known: list[tuple[JobRequirement, RequirementAlignment, float]] = []

        for requirement in selected:
            alignment = alignments.get(requirement.requirement_id)

            if alignment is None:
                continue

            value = self._ALIGNMENT_VALUES.get(alignment.status)

            # UNKNOWN is deliberately excluded. Absence of evidence
            # does not prove absence of the capability.
            if value is None:
                continue

            known.append((requirement, alignment, value))

        if not known:
            return 0.0, False

        score = sum(value for _, _, value in known) / len(known)

        per_requirement_weight = (
            self._WEIGHTS[dimension] / len(known)
        )

        for requirement, alignment, value in known:
            contributions.append(
                ScoreContribution(
                    contribution_id=(
                        f"{dimension}:{requirement.requirement_id}"
                    ),
                    dimension=dimension,
                    source_type="requirement_alignment",
                    source_id=requirement.requirement_id,
                    score=value,
                    weight=per_requirement_weight,
                    contribution=value * per_requirement_weight,
                    rationale=self._requirement_rationale(
                        requirement,
                        alignment,
                    ),
                    requirement_type=requirement.requirement_type.value,
                )
            )

        return score, True

    def _score_domain(
        self,
        *,
        job_profile: JobProfile,
        job_skills: list,
        matching: MatchingResult,
        contributions: list[ScoreContribution],
    ) -> tuple[float, bool]:
        domain_names = {
            str(name).strip().lower()
            for name in job_profile.domain_skills
            if str(name).strip()
        }

        if not domain_names:
            return 0.0, False

        job_skill_by_id = {
            skill.skill_id: skill
            for skill in job_skills
        }

        domain_matches: dict[str, SkillMatch] = {}

        for match in matching.skill_matches:
            job_skill = job_skill_by_id.get(match.job_skill_id)

            if job_skill is None:
                continue

            if (
                job_skill.canonical_name.lower() in domain_names
                or job_skill.display_name.lower() in domain_names
            ):
                existing = domain_matches.get(match.job_skill_id)

                if existing is None or match.similarity > existing.similarity:
                    domain_matches[match.job_skill_id] = match

        if not domain_matches:
            return 0.0, False

        values: list[float] = []

        relationship_values = {
            "exact": 1.0,
            "strong_semantic": 1.0,
            "partial": 0.5,
            "related": 0.5,
            "unmatched": 0.0,
        }

        for job_skill_id, match in domain_matches.items():
            value = relationship_values[match.relationship.value]
            values.append(value)

            contributions.append(
                ScoreContribution(
                    contribution_id=f"domain:{job_skill_id}",
                    dimension="domain",
                    source_type="skill_match",
                    source_id=job_skill_id,
                    score=value,
                    weight=self._WEIGHTS["domain"] / len(domain_matches),
                    contribution=(
                        value
                        * self._WEIGHTS["domain"]
                        / len(domain_matches)
                    ),
                    rationale=(
                        "Domain contribution derived from the existing "
                        "Phase 5 skill match; matching strength remains "
                        "separate from confidence."
                    ),
                )
            )

        return sum(values) / len(values), True

    @staticmethod
    def _weighted_skill_score(
        *,
        required_score: float,
        required_available: bool,
        preferred_score: float,
        preferred_available: bool,
    ) -> float:
        weights = []
        values = []

        if required_available:
            weights.append(0.50)
            values.append(required_score)

        if preferred_available:
            weights.append(0.15)
            values.append(preferred_score)

        if not weights:
            return 0.0

        return sum(value * weight for value, weight in zip(values, weights)) / sum(
            weights
        )

    @staticmethod
    def _requirement_rationale(
        requirement: JobRequirement,
        alignment: RequirementAlignment,
    ) -> str:
        return (
            f"{requirement.requirement_type.value} "
            f"{requirement.category.value} requirement is "
            f"{alignment.status.value}; "
            f"{alignment.rationale or 'alignment status supplied by Phase 5.'}"
        )

    @staticmethod
    def _build_confidence(
        *,
        requirements: list[JobRequirement],
        matching: MatchingResult,
        available_dimensions: int,
    ) -> Confidence:
        alignment_scores = [
            alignment.confidence.score
            for alignment in matching.requirement_alignments
            if alignment.confidence is not None
        ]

        requirement_scores = [
            requirement.confidence.score
            for requirement in requirements
            if requirement.confidence is not None
        ]

        components: dict[str, float] = {
            "available_dimensions": float(available_dimensions),
        }

        candidates = alignment_scores + requirement_scores

        if matching.confidence is not None:
            candidates.append(matching.confidence.score)

        if candidates:
            score = max(0.0, min(1.0, sum(candidates) / len(candidates)))
        else:
            score = 0.0

        if score >= 0.85:
            level = ConfidenceLevel.HIGH
        elif score >= 0.65:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        if alignment_scores:
            components["alignment_confidence"] = (
                sum(alignment_scores) / len(alignment_scores)
            )

        if requirement_scores:
            components["requirement_confidence"] = (
                sum(requirement_scores) / len(requirement_scores)
            )

        return Confidence(
            score=score,
            level=level,
            components=components,
            rationale="derived_from_existing_requirement_and_matching_confidence",
        )
