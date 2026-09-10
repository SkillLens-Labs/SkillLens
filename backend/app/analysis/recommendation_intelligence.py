from __future__ import annotations

from hashlib import sha256

from backend.app.domain.career import CareerIntelligence
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.gaps import SkillAnalysis, SkillGap
from backend.app.domain.job import JobProfile
from backend.app.domain.matching import JobRequirement, JobRequirementCategory, MatchingResult
from backend.app.domain.recommendations import (
    Recommendation,
    RecommendationEffort,
    RecommendationImpact,
    RecommendationPriority,
    RecommendationType,
)
from backend.app.domain.resume import ResumeProfile
from backend.app.domain.scoring import ScoringResult
from backend.app.domain.xai import XAIResult


ENGINE_VERSION = "recommendation-intelligence-v1"


class RecommendationIntelligence:
    """
    Deterministic Phase 8 recommendation engine.

    This component consumes authoritative outputs from earlier analytical
    phases and converts them into evidence-backed recommendations.

    It does not:
    - extract or normalize skills
    - perform skill matching
    - classify gaps
    - calculate candidate scores
    - calculate career fit
    - calculate confidence for upstream analytical results
    - call an LLM
    """

    ENGINE_VERSION = ENGINE_VERSION

    def generate(
        self,
        *,
        resume_profile: ResumeProfile,
        skill_analysis: SkillAnalysis | None = None,
        career_intelligence: CareerIntelligence | None = None,
        job_profile: JobProfile | None = None,
        matching: MatchingResult | None = None,
        scoring: ScoringResult | None = None,
        xai: XAIResult | None = None,
        requirements: list[JobRequirement] | tuple[JobRequirement, ...] = (),
    ) -> list[Recommendation]:
        """
        Generate deterministic recommendations from existing intelligence.

        Output ordering is deterministic and independent of timestamps,
        UUIDs, hash randomization, or LLM output.
        """
        requirement_by_id = {
            requirement.requirement_id: requirement
            for requirement in requirements
        }

        recommendations: list[Recommendation] = []

        if skill_analysis is not None:
            recommendations.extend(
                self._recommend_for_gaps(
                    skill_analysis=skill_analysis,
                    job_profile=job_profile,
                    matching=matching,
                    scoring=scoring,
                    xai=xai,
                    requirement_by_id=requirement_by_id,
                )
            )

        if matching is not None and requirement_by_id:
            recommendations.extend(
                self._recommend_for_structured_requirements(
                    matching=matching,
                    requirement_by_id=requirement_by_id,
                )
            )

        if career_intelligence is not None:
            recommendations.extend(
                self._recommend_for_career(
                    career_intelligence=career_intelligence,
                )
            )

        recommendations.extend(
            self._recommend_for_resume(
                resume_profile=resume_profile,
            )
        )

        recommendations = self._deduplicate(recommendations)
        recommendations.sort(key=self._sort_key)

        return recommendations

    def _recommend_for_gaps(
        self,
        *,
        skill_analysis: SkillAnalysis,
        job_profile: JobProfile | None,
        matching: MatchingResult | None,
        scoring: ScoringResult | None,
        xai: XAIResult | None,
        requirement_by_id: dict[str, JobRequirement],
    ) -> list[Recommendation]:
        recommendations: list[Recommendation] = []

        for gap in skill_analysis.gaps:
            if gap.match_status == "matched":
                continue

            target = gap.target_skill_name.strip()
            if not target:
                continue

            requirement = requirement_by_id.get(gap.requirement_id)

            priority_score = self._priority_score(gap)
            impact_score = self._impact_score(gap)

            recommendation_type = self._recommendation_type(
                gap=gap,
                requirement=requirement,
            )

            recommendation = Recommendation(
                recommendation_id=self._stable_id(
                    recommendation_type.value,
                    target,
                    gap.gap_id,
                ),
                type=recommendation_type,
                title=self._gap_title(
                    recommendation_type,
                    target,
                ),
                target_skill=target,
                priority=self._priority(priority_score),
                rationale=self._gap_rationale(gap),
                expected_impact=self._impact(impact_score),
                effort=self._effort(gap),
                evidence=list(gap.evidence),
                related_gap_ids=[gap.gap_id],
                confidence=self._recommendation_confidence(gap),
                priority_score=priority_score,
                impact_score=impact_score,
                source_engine=self.ENGINE_VERSION,
            )

            recommendations.append(recommendation)

        return recommendations

    def _recommend_for_structured_requirements(
        self,
        *,
        matching: MatchingResult,
        requirement_by_id: dict[str, JobRequirement],
    ) -> list[Recommendation]:
        recommendations: list[Recommendation] = []

        for alignment in matching.requirement_alignments:
            if alignment.status.value == "matched":
                continue

            requirement = requirement_by_id.get(alignment.requirement_id)

            if requirement is None:
                continue

            if requirement.category == JobRequirementCategory.SKILL:
                continue

            priority_score = self._structured_priority_score(
                requirement=requirement,
                status=alignment.status.value,
            )

            impact_score = self._structured_impact_score(
                requirement=requirement,
                status=alignment.status.value,
            )

            recommendation_type = self._structured_recommendation_type(
                requirement.category,
            )

            title = self._structured_title(
                requirement=requirement,
                recommendation_type=recommendation_type,
            )

            rationale = self._structured_rationale(
                requirement=requirement,
                status=alignment.status.value,
            )

            recommendation = Recommendation(
                recommendation_id=self._stable_id(
                    recommendation_type.value,
                    requirement.requirement_id,
                ),
                type=recommendation_type,
                title=title,
                target_skill=None,
                priority=self._priority(priority_score),
                rationale=rationale,
                expected_impact=self._impact(impact_score),
                effort=(
                    RecommendationEffort.HIGH
                    if alignment.status.value == "unmatched"
                    else RecommendationEffort.MEDIUM
                ),
                evidence=list(alignment.evidence),
                related_gap_ids=[],
                confidence=(
                    alignment.confidence
                    or requirement.confidence
                    or self._static_confidence(
                        score=0.70,
                        rationale=(
                            "Recommendation confidence is based on the "
                            "structured requirement alignment."
                        ),
                    )
                ),
                priority_score=priority_score,
                impact_score=impact_score,
                source_engine=self.ENGINE_VERSION,
            )

            recommendations.append(recommendation)

        return recommendations

    def _recommend_for_career(
        self,
        *,
        career_intelligence: CareerIntelligence,
    ) -> list[Recommendation]:
        recommendations: list[Recommendation] = []

        for role_fit in career_intelligence.role_fit:
            if role_fit.fit_score < 60:
                continue

            role = role_fit.role.strip()
            if not role:
                continue

            score = min(100.0, max(0.0, role_fit.fit_score))

            recommendations.append(
                Recommendation(
                    recommendation_id=self._stable_id(
                        RecommendationType.CAREER.value,
                        role,
                    ),
                    type=RecommendationType.CAREER,
                    title=f"Explore {role} career path",
                    rationale=role_fit.rationale,
                    expected_impact=self._impact(score),
                    effort=RecommendationEffort.MEDIUM,
                    evidence=list(role_fit.evidence),
                    confidence=role_fit.confidence,
                    priority=self._priority(score),
                    priority_score=score,
                    impact_score=score,
                    source_engine=self.ENGINE_VERSION,
                )
            )

        return recommendations

    def _recommend_for_resume(
        self,
        *,
        resume_profile: ResumeProfile,
    ) -> list[Recommendation]:
        recommendations: list[Recommendation] = []

        if not resume_profile.candidate_summary:
            recommendations.append(
                Recommendation(
                    recommendation_id=self._stable_id(
                        RecommendationType.RESUME.value,
                        "summary",
                    ),
                    type=RecommendationType.RESUME,
                    title="Add a professional summary",
                    rationale=(
                        "The resume profile does not contain a professional "
                        "summary. Adding a concise, role-focused summary can "
                        "improve recruiter readability and positioning."
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    expected_impact=RecommendationImpact.MEDIUM,
                    effort=RecommendationEffort.LOW,
                    priority_score=50.0,
                    impact_score=55.0,
                    confidence=self._static_confidence(
                        score=0.95,
                        rationale="The recommendation is based on a direct absence check.",
                    ),
                    source_engine=self.ENGINE_VERSION,
                )
            )

        if not resume_profile.skills:
            recommendations.append(
                Recommendation(
                    recommendation_id=self._stable_id(
                        RecommendationType.RESUME.value,
                        "skills",
                    ),
                    type=RecommendationType.RESUME,
                    title="Strengthen the skills section",
                    rationale=(
                        "The resume profile does not contain extracted skills. "
                        "A clear skills section should surface relevant technical "
                        "and domain capabilities."
                    ),
                    priority=RecommendationPriority.HIGH,
                    expected_impact=RecommendationImpact.HIGH,
                    effort=RecommendationEffort.LOW,
                    priority_score=75.0,
                    impact_score=80.0,
                    confidence=self._static_confidence(
                        score=0.95,
                        rationale="The recommendation is based on a direct absence check.",
                    ),
                    source_engine=self.ENGINE_VERSION,
                )
            )

        return recommendations

    @staticmethod
    def _recommendation_type(
        *,
        gap: SkillGap,
        requirement: JobRequirement | None,
    ) -> RecommendationType:
        if requirement is not None:
            if requirement.category == JobRequirementCategory.CERTIFICATION:
                return RecommendationType.CERTIFICATION

            if requirement.category == JobRequirementCategory.EXPERIENCE:
                return RecommendationType.PROJECT

            if requirement.category == JobRequirementCategory.EDUCATION:
                return RecommendationType.CAREER

        return RecommendationType.LEARNING

    @staticmethod
    def _structured_recommendation_type(
        category: JobRequirementCategory,
    ) -> RecommendationType:
        if category == JobRequirementCategory.CERTIFICATION:
            return RecommendationType.CERTIFICATION

        if category == JobRequirementCategory.EXPERIENCE:
            return RecommendationType.PROJECT

        if category == JobRequirementCategory.EDUCATION:
            return RecommendationType.CAREER

        return RecommendationType.JOB_ALIGNMENT

    @staticmethod
    def _structured_title(
        *,
        requirement: JobRequirement,
        recommendation_type: RecommendationType,
    ) -> str:
        text = requirement.text.strip()

        if requirement.category == JobRequirementCategory.CERTIFICATION:
            return f"Address certification requirement: {text}"

        if requirement.category == JobRequirementCategory.EXPERIENCE:
            return f"Build experience for: {text}"

        if requirement.category == JobRequirementCategory.EDUCATION:
            return f"Address education requirement: {text}"

        return f"Improve job alignment: {text}"

    @staticmethod
    def _structured_rationale(
        *,
        requirement: JobRequirement,
        status: str,
    ) -> str:
        category = requirement.category.value
        requirement_type = requirement.requirement_type.value

        if status == "partial":
            status_text = (
                "The candidate has partial alignment with this requirement."
            )
        elif status == "unknown":
            status_text = (
                "The available resume evidence is insufficient to confirm "
                "alignment with this requirement."
            )
        else:
            status_text = (
                "The candidate is not currently aligned with this requirement."
            )

        priority_text = (
            "Because it is required, addressing it should be prioritized."
            if requirement_type == "required"
            else
            "Because it is preferred, addressing it can strengthen overall "
            "job alignment."
        )

        return (
            f"{status_text} The requirement is classified as {category}. "
            f"{priority_text}"
        )

    @staticmethod
    def _structured_priority_score(
        *,
        requirement: JobRequirement,
        status: str,
    ) -> float:
        score = 45.0

        if requirement.requirement_type.value == "required":
            score += 25.0
        else:
            score += 10.0

        if status == "unmatched":
            score += 15.0
        elif status == "partial":
            score += 5.0

        category_bonus = {
            JobRequirementCategory.CERTIFICATION: 5.0,
            JobRequirementCategory.EXPERIENCE: 5.0,
            JobRequirementCategory.EDUCATION: 3.0,
        }

        score += category_bonus.get(requirement.category, 0.0)

        return min(100.0, score)

    @staticmethod
    def _structured_impact_score(
        *,
        requirement: JobRequirement,
        status: str,
    ) -> float:
        score = 45.0

        if requirement.requirement_type.value == "required":
            score += 30.0
        else:
            score += 10.0

        if status == "unmatched":
            score += 15.0
        elif status == "partial":
            score += 8.0

        category_bonus = {
            JobRequirementCategory.CERTIFICATION: 5.0,
            JobRequirementCategory.EXPERIENCE: 5.0,
            JobRequirementCategory.EDUCATION: 3.0,
        }

        score += category_bonus.get(requirement.category, 0.0)

        return min(100.0, score)

    @staticmethod
    def _gap_title(
        recommendation_type: RecommendationType,
        target: str,
    ) -> str:
        if recommendation_type == RecommendationType.CERTIFICATION:
            return f"Develop certification readiness for {target}"

        return f"Build proficiency in {target}"

    @staticmethod
    def _gap_rationale(gap: SkillGap) -> str:
        requirement = gap.requirement_type.lower()

        if gap.match_status == "partial":
            base = (
                f"{gap.target_skill_name} is partially aligned with the "
                "target requirement."
            )
        else:
            base = (
                f"{gap.target_skill_name} is not sufficiently represented "
                "in the current resume profile."
            )

        if requirement == "required":
            return (
                f"{base} It is a required job capability, so addressing this "
                "gap should be prioritized."
            )

        return (
            f"{base} It is a preferred capability, so improving it can "
            "strengthen overall job alignment."
        )

    @staticmethod
    def _priority_score(gap: SkillGap) -> float:
        requirement = gap.requirement_type.lower()
        severity = (gap.severity or "").lower()
        status = gap.match_status.lower()

        score = 45.0

        if requirement == "required":
            score += 25.0
        elif requirement == "preferred":
            score += 10.0

        if status == "unmatched":
            score += 15.0
        elif status == "partial":
            score += 5.0

        if severity == "high":
            score += 15.0
        elif severity == "medium":
            score += 8.0
        elif severity == "low":
            score += 2.0

        return min(100.0, score)

    @staticmethod
    def _impact_score(gap: SkillGap) -> float:
        requirement = gap.requirement_type.lower()
        status = gap.match_status.lower()

        score = 45.0

        if requirement == "required":
            score += 30.0
        elif requirement == "preferred":
            score += 10.0

        if status == "unmatched":
            score += 15.0
        elif status == "partial":
            score += 8.0

        return min(100.0, score)

    @staticmethod
    def _priority(score: float) -> RecommendationPriority:
        if score >= 90:
            return RecommendationPriority.CRITICAL
        if score >= 75:
            return RecommendationPriority.HIGH
        if score >= 50:
            return RecommendationPriority.MEDIUM
        return RecommendationPriority.LOW

    @staticmethod
    def _impact(score: float) -> RecommendationImpact:
        if score >= 75:
            return RecommendationImpact.HIGH
        if score >= 50:
            return RecommendationImpact.MEDIUM
        return RecommendationImpact.LOW

    @staticmethod
    def _effort(gap: SkillGap) -> RecommendationEffort:
        if gap.match_status.lower() == "unmatched":
            return RecommendationEffort.HIGH

        return RecommendationEffort.MEDIUM

    @staticmethod
    def _recommendation_confidence(gap: SkillGap) -> Confidence:
        if gap.confidence is not None:
            return gap.confidence

        similarity = gap.similarity
        if similarity is None:
            score = 0.70
        else:
            score = min(1.0, max(0.0, similarity))

        if score >= 0.80:
            level = ConfidenceLevel.HIGH
        elif score >= 0.55:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        return Confidence(
            score=score,
            level=level,
            components={
                "gap_similarity": score,
            },
            rationale=(
                "Recommendation confidence is derived from the existing "
                "gap confidence or similarity signal."
            ),
        )

    @staticmethod
    def _static_confidence(
        *,
        score: float,
        rationale: str,
    ) -> Confidence:
        level = (
            ConfidenceLevel.HIGH
            if score >= 0.80
            else ConfidenceLevel.MEDIUM
            if score >= 0.55
            else ConfidenceLevel.LOW
        )

        return Confidence(
            score=score,
            level=level,
            components={"direct_rule": score},
            rationale=rationale,
        )

    @staticmethod
    def _stable_id(*parts: str) -> str:
        normalized = "|".join(
            part.strip().lower()
            for part in parts
        )
        digest = sha256(normalized.encode("utf-8")).hexdigest()[:16]
        return f"rec-{digest}"

    @staticmethod
    def _deduplicate(
        recommendations: list[Recommendation],
    ) -> list[Recommendation]:
        unique: dict[str, Recommendation] = {}

        for recommendation in recommendations:
            existing = unique.get(recommendation.recommendation_id)

            if existing is None:
                unique[recommendation.recommendation_id] = recommendation
                continue

            if (
                recommendation.priority_score,
                recommendation.impact_score,
            ) > (
                existing.priority_score,
                existing.impact_score,
            ):
                unique[recommendation.recommendation_id] = recommendation

        return list(unique.values())

    @staticmethod
    def _sort_key(
        recommendation: Recommendation,
    ) -> tuple[float, float, str, str]:
        return (
            -recommendation.priority_score,
            -recommendation.impact_score,
            recommendation.type.value,
            recommendation.recommendation_id,
        )