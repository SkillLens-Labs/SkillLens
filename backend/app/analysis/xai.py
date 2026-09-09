from __future__ import annotations

from statistics import mean

from backend.app.domain.gaps import SkillAnalysis, SkillGap
from backend.app.domain.matching import MatchingResult
from backend.app.domain.scoring import ScoringResult
from backend.app.domain.xai import (
    EvidenceMapEntry,
    SkillExplanation,
    XAIResult,
)


class XAIAnalyzer:
    """
    Deterministic explainability layer for Phase 6.

    This analyzer explains existing Phase 5 and Phase 6 results.
    It does not perform matching, gap detection, scoring, or
    recommendation generation.
    """

    ENGINE_VERSION = "phase6-xai-v1"

    def explain(
        self,
        *,
        scoring: ScoringResult | None,
        skill_analysis: SkillAnalysis,
        matching: MatchingResult | None,
        resume_skills=None,
        job_skills=None,
    ) -> XAIResult:
        matched_explanations = self._matched_skill_explanations(
            skill_analysis=skill_analysis,
            matching=matching,
            resume_skills=resume_skills or [],
            job_skills=job_skills or [],
        )

        partial_explanations = self._gap_explanations(
            skill_analysis.gaps,
            gap_type="partial",
        )

        missing_explanations = self._gap_explanations(
            skill_analysis.gaps,
            gap_type="unmatched",
        )

        evidence_map = self._build_evidence_map(
            skill_analysis=skill_analysis,
            matching=matching,
        )

        strengths = self._build_strengths(
            skill_analysis=skill_analysis,
            matching=matching,
        )

        weaknesses = self._build_weaknesses(
            skill_analysis=skill_analysis,
        )

        score_explanation = self._build_score_explanation(scoring)

        overall_explanation = self._build_overall_explanation(
            scoring=scoring,
            skill_analysis=skill_analysis,
        )

        confidence = self._aggregate_confidence(
            scoring=scoring,
            skill_analysis=skill_analysis,
        )

        return XAIResult(
            overall_explanation=overall_explanation,
            score_explanation=score_explanation,
            strengths=strengths,
            weaknesses=weaknesses,
            matched_skill_explanations=matched_explanations,
            missing_skill_explanations=missing_explanations,
            partial_match_explanations=partial_explanations,
            evidence_map=evidence_map,
            confidence=confidence,
        )

    @staticmethod
    def _matched_skill_explanations(
        *,
        skill_analysis: SkillAnalysis,
        matching: MatchingResult | None,
        resume_skills,
        job_skills,
    ) -> list[SkillExplanation]:
        if matching is None:
            return []

        resume_by_id = {
            skill.skill_id: skill
            for skill in resume_skills
        }

        job_by_id = {
            skill.skill_id: skill
            for skill in job_skills
        }

        matched_names = {
            name.casefold()
            for name in skill_analysis.matched_skills
        }

        explanations: list[SkillExplanation] = []

        for match in matching.skill_matches:
            resume_skill = resume_by_id.get(match.resume_skill_id)
            job_skill = job_by_id.get(match.job_skill_id)

            resume_name = (
                resume_skill.display_name
                if resume_skill is not None
                else match.resume_skill_id
            )

            job_name = (
                job_skill.display_name
                if job_skill is not None
                else match.job_skill_id
            )

            if matched_names:
                candidate_names = {
                    resume_name.casefold(),
                    job_name.casefold(),
                }

                if not candidate_names.intersection(matched_names):
                    continue

            evidence = list(match.evidence)

            if not evidence and resume_skill is not None:
                evidence = list(resume_skill.evidence)

            explanation = (
                f"{resume_name} matches the job requirement "
                f"{job_name} with a {match.relationship.value} relationship "
                f"and similarity {match.similarity:.2f}."
            )

            explanations.append(
                SkillExplanation(
                    skill_id=match.resume_skill_id,
                    explanation=explanation,
                    evidence=evidence,
                    confidence=match.confidence,
                )
            )

        return explanations

    @staticmethod
    def _gap_explanations(
        gaps: list[SkillGap],
        *,
        gap_type: str,
    ) -> list[SkillExplanation]:
        explanations: list[SkillExplanation] = []

        for gap in gaps:
            if gap.gap_type != gap_type:
                continue

            similarity_text = (
                f" Similarity is {gap.similarity:.2f}."
                if gap.similarity is not None
                else ""
            )

            rationale = gap.rationale or (
                f"The requirement is classified as {gap.match_status}."
            )

            explanation = (
                f"{gap.target_skill_name} is classified as "
                f"{gap.match_status} for this {gap.requirement_type} "
                f"requirement.{similarity_text} {rationale}"
            )

            explanations.append(
                SkillExplanation(
                    skill_id=gap.target_skill_id,
                    explanation=explanation.strip(),
                    evidence=list(gap.evidence),
                    confidence=gap.confidence,
                )
            )

        return explanations

    @staticmethod
    def _build_evidence_map(
        *,
        skill_analysis: SkillAnalysis,
        matching: MatchingResult | None,
    ) -> list[EvidenceMapEntry]:
        entries: list[EvidenceMapEntry] = []

        for gap in skill_analysis.gaps:
            entries.append(
                EvidenceMapEntry(
                    result_type="skill_gap",
                    result_id=gap.gap_id,
                    evidence=list(gap.evidence),
                )
            )

        if matching is not None:
            for match in matching.skill_matches:
                if match.evidence:
                    entries.append(
                        EvidenceMapEntry(
                            result_type="skill_match",
                            result_id=(
                                f"{match.resume_skill_id}:"
                                f"{match.job_skill_id}"
                            ),
                            evidence=list(match.evidence),
                        )
                    )

        return entries

    @staticmethod
    def _build_strengths(
        *,
        skill_analysis: SkillAnalysis,
        matching: MatchingResult | None,
    ) -> list[str]:
        strengths: list[str] = []

        for skill in skill_analysis.matched_skills:
            strengths.append(f"Matched skill: {skill}.")

        if matching is not None:
            strong_matches = [
                match
                for match in matching.skill_matches
                if match.relationship.value in {
                    "exact",
                    "strong_semantic",
                }
            ]

            if strong_matches:
                strengths.append(
                    f"{len(strong_matches)} strong skill match(es) "
                    "support the alignment."
                )

        return strengths

    @staticmethod
    def _build_weaknesses(
        *,
        skill_analysis: SkillAnalysis,
    ) -> list[str]:
        weaknesses: list[str] = []

        for skill in skill_analysis.missing_skills:
            weaknesses.append(f"Unmatched skill requirement: {skill}.")

        for skill in skill_analysis.partial_matches:
            weaknesses.append(f"Partial skill match: {skill}.")

        return weaknesses

    @staticmethod
    def _build_score_explanation(
        scoring: ScoringResult | None,
    ) -> str | None:
        if scoring is None:
            return None

        dimensions = scoring.dimension_scores

        if not dimensions:
            return (
                f"The overall score is {scoring.overall_score:.2f} out of 100. "
                "No scored dimensions were available."
            )

        dimension_text = "; ".join(
            (
                f"{dimension.dimension}={dimension.score:.2f}/100 "
                f"(weight {dimension.weight:.2f})"
            )
            for dimension in dimensions
        )

        contribution_text = ""

        if scoring.contributions:
            contribution_text = " Contributions: " + "; ".join(
                (
                    f"{contribution.source_id} contributes "
                    f"{contribution.contribution:.4f} "
                    f"through {contribution.dimension} "
                    f"because {contribution.rationale}"
                )
                for contribution in scoring.contributions
            ) + "."

        return (
            f"The overall score is {scoring.overall_score:.2f} out of 100. "
            f"Available dimensions are: {dimension_text}."
            f"{contribution_text}"
        )

    @staticmethod
    def _build_overall_explanation(
        *,
        scoring: ScoringResult | None,
        skill_analysis: SkillAnalysis,
    ) -> str:
        if scoring is None:
            return (
                "Explainability is based on the available skill-analysis "
                "results; no scoring result was provided."
            )

        matched = len(skill_analysis.matched_skills)
        partial = len(skill_analysis.partial_matches)
        missing = len(skill_analysis.missing_skills)

        return (
            f"The analysis produced an overall score of "
            f"{scoring.overall_score:.2f} out of 100. "
            f"Skill results include {matched} matched, {partial} partial, "
            f"and {missing} unmatched skill requirement(s). "
            "The explanation reflects existing analytical results and "
            "does not recalculate them."
        )

    @staticmethod
    def _aggregate_confidence(
        *,
        scoring: ScoringResult | None,
        skill_analysis: SkillAnalysis,
    ):
        scores: list[float] = []

        if scoring is not None and scoring.confidence is not None:
            scores.append(scoring.confidence.score)

        for gap in skill_analysis.gaps:
            if gap.confidence is not None:
                scores.append(gap.confidence.score)

        if not scores:
            return None

        score = mean(scores)

        if score >= 0.85:
            level = "high"
        elif score >= 0.65:
            level = "medium"
        else:
            level = "low"

        from backend.app.domain.confidence import Confidence, ConfidenceLevel

        return Confidence(
            score=score,
            level=ConfidenceLevel(level),
            components={
                "source_count": float(len(scores)),
            },
            rationale=(
                "Aggregated from existing scoring and gap confidence "
                "values; similarity is not used as confidence."
            ),
        )
