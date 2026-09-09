from __future__ import annotations

from backend.app.domain.gaps import SkillAnalysis, SkillGap
from backend.app.domain.matching import (
    JobRequirement,
    JobRequirementCategory,
    MatchingResult,
    RequirementMatchStatus,
    SkillMatch,
)
from backend.app.domain.skill import Skill


class GapAnalyzer:
    """
    Build deterministic skill-gap results from existing Phase 5 outputs.

    Phase 6 responsibilities:
    - consume existing requirement alignments
    - preserve required/preferred classification
    - preserve match status
    - preserve evidence and confidence
    - preserve existing similarity when an unambiguous SkillMatch exists
    - classify partial, unmatched, and unknown skill requirements

    This analyzer does NOT:
    - perform semantic matching
    - perform requirement alignment
    - calculate scores
    - generate recommendations
    - recalculate Phase 5 results
    """

    ENGINE_VERSION = "phase6-gap-analysis-v1"

    _GAP_TYPES = {
        RequirementMatchStatus.PARTIAL: "partial",
        RequirementMatchStatus.UNMATCHED: "unmatched",
        RequirementMatchStatus.UNKNOWN: "unknown",
    }

    _SEVERITY = {
        RequirementMatchStatus.PARTIAL: "medium",
        RequirementMatchStatus.UNMATCHED: "high",
        RequirementMatchStatus.UNKNOWN: "unknown",
    }

    def analyze(
        self,
        *,
        requirements: list[JobRequirement] | tuple[JobRequirement, ...],
        matching: MatchingResult,
        resume_skills: list[Skill] | tuple[Skill, ...],
        job_skills: list[Skill] | tuple[Skill, ...],
    ) -> SkillAnalysis:
        requirement_by_id = {
            requirement.requirement_id: requirement
            for requirement in requirements
        }

        resume_skill_by_id = {
            skill.skill_id: skill
            for skill in resume_skills
        }

        job_skill_by_id = {
            skill.skill_id: skill
            for skill in job_skills
        }

        alignments_by_id = {
            alignment.requirement_id: alignment
            for alignment in matching.requirement_alignments
        }

        skill_matches = tuple(matching.skill_matches)

        extracted_skills = self._unique_names(resume_skills)
        matched_skills: list[str] = []
        partial_matches: list[str] = []
        missing_skills: list[str] = []
        gaps: list[SkillGap] = []

        for requirement in requirements:
            if requirement.category != JobRequirementCategory.SKILL:
                continue

            alignment = alignments_by_id.get(requirement.requirement_id)

            if alignment is None:
                # No alignment exists, therefore Phase 6 cannot infer
                # a missing skill from absence of an alignment.
                continue

            status = alignment.status

            target_skill = self._resolve_target_skill(
                requirement=requirement,
                job_skill_by_id=job_skill_by_id,
            )

            if target_skill is None:
                target_skill_id = (
                    requirement.skill_id
                    or f"requirement:{requirement.requirement_id}"
                )
                target_skill_name = (
                    requirement.canonical_name
                    or requirement.text.strip()
                )
            else:
                target_skill_id = target_skill.skill_id
                target_skill_name = target_skill.display_name

            skill_match = self._find_existing_match(
                requirement=requirement,
                target_skill_id=target_skill_id,
                skill_matches=skill_matches,
                resume_skill_by_id=resume_skill_by_id,
                job_skill_by_id=job_skill_by_id,
            )

            if status == RequirementMatchStatus.MATCHED:
                matched_skills.append(target_skill_name)
                continue

            gap_type = self._GAP_TYPES.get(status)

            if gap_type is None:
                continue

            gap = SkillGap(
                gap_id=f"gap-{requirement.requirement_id}",
                requirement_id=requirement.requirement_id,
                requirement_type=requirement.requirement_type.value,
                target_skill_id=target_skill_id,
                target_skill_name=target_skill_name,
                match_status=status.value,
                gap_type=gap_type,
                severity=self._SEVERITY.get(status),
                similarity=(
                    skill_match.similarity
                    if skill_match is not None
                    else None
                ),
                rationale=alignment.rationale,
                evidence=list(alignment.evidence),
                confidence=alignment.confidence,
            )

            gaps.append(gap)

            if status == RequirementMatchStatus.PARTIAL:
                partial_matches.append(target_skill_name)
            elif status == RequirementMatchStatus.UNMATCHED:
                missing_skills.append(target_skill_name)

        return SkillAnalysis(
            extracted_skills=extracted_skills,
            matched_skills=self._unique_strings(matched_skills),
            partial_matches=self._unique_strings(partial_matches),
            missing_skills=self._unique_strings(missing_skills),
            transferable_skills=[],
            gaps=gaps,
        )

    @staticmethod
    def _resolve_target_skill(
        *,
        requirement: JobRequirement,
        job_skill_by_id: dict[str, Skill],
    ) -> Skill | None:
        if requirement.skill_id:
            skill = job_skill_by_id.get(requirement.skill_id)
            if skill is not None:
                return skill

        if requirement.canonical_name:
            canonical = requirement.canonical_name.casefold()
            for skill in job_skill_by_id.values():
                if skill.canonical_name.casefold() == canonical:
                    return skill

        return None

    @staticmethod
    def _find_existing_match(
        *,
        requirement: JobRequirement,
        target_skill_id: str,
        skill_matches: tuple[SkillMatch, ...],
        resume_skill_by_id: dict[str, Skill],
        job_skill_by_id: dict[str, Skill],
    ) -> SkillMatch | None:
        candidates = [
            match
            for match in skill_matches
            if match.job_skill_id == target_skill_id
        ]

        if len(candidates) == 1:
            return candidates[0]

        if len(candidates) > 1:
            # Select the strongest existing Phase 5 match without
            # recalculating semantic similarity.
            return max(
                candidates,
                key=lambda match: (
                    GapAnalyzer._relationship_rank(
                        match.relationship.value
                    ),
                    match.similarity,
                ),
            )

        # If the requirement has no resolved target skill, use its
        # canonical name only for deterministic identity matching.
        if requirement.canonical_name:
            canonical = requirement.canonical_name.casefold()
            matching_job_ids = {
                skill.skill_id
                for skill in job_skill_by_id.values()
                if skill.canonical_name.casefold() == canonical
            }

            candidates = [
                match
                for match in skill_matches
                if match.job_skill_id in matching_job_ids
            ]

            if candidates:
                return max(
                    candidates,
                    key=lambda match: (
                        GapAnalyzer._relationship_rank(
                            match.relationship.value
                        ),
                        match.similarity,
                    ),
                )

        return None

    @staticmethod
    def _relationship_rank(relationship: str) -> int:
        return {
            "exact": 4,
            "strong_semantic": 3,
            "partial": 2,
            "related": 1,
            "unmatched": 0,
        }.get(relationship, 0)

    @staticmethod
    def _unique_names(skills: list[Skill] | tuple[Skill, ...]) -> list[str]:
        return GapAnalyzer._unique_strings(
            [skill.display_name for skill in skills]
        )

    @staticmethod
    def _unique_strings(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []

        for value in values:
            if value in seen:
                continue
            seen.add(value)
            result.append(value)

        return result
