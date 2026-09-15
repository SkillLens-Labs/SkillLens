from __future__ import annotations

import re

from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.matching import (
    JobRequirement,
    JobRequirementCategory,
    RequirementAlignment,
    RequirementMatchStatus,
    SkillMatch,
)
from backend.app.domain.skill import Skill
from backend.app.analysis.resume_structure import (
    ResumeSectionType,
    StructuredResume,
)


class RequirementAligner:
    """
    Align job requirements with resume evidence and existing skill matches.

    Phase 5 only:
    - produces requirement-level alignment status
    - preserves evidence and confidence
    - does not calculate candidate-job scores
    - does not generate explanations or recommendations
    """

    ENGINE_VERSION = "phase5-requirement-aligner-v1"

    _EXPERIENCE_EVIDENCE_SECTIONS = (
        ResumeSectionType.EXPERIENCE,
        ResumeSectionType.PROJECTS,
        ResumeSectionType.SKILLS,
    )

    _EXPERIENCE_CONCEPT_ALIASES = {
        "etl": {"etl", "elt", "etl/elt"},
        "data_pipelines": {
            "data pipeline",
            "data pipelines",
            "pipeline",
            "pipelines",
        },
        "data_validation": {
            "data validation",
            "validation",
            "validate",
        },
        "sql": {"sql", "postgresql", "mysql", "sqlite"},
        "relational_databases": {
            "relational database",
            "relational databases",
            "postgresql",
            "mysql",
            "sqlite",
        },
        "rest_backend": {
            "rest api",
            "rest apis",
            "rest",
            "backend",
            "fastapi",
            "flask",
            "django",
        },
        "docker_linux": {
            "docker",
            "linux",
        },
        "testing": {
            "testing",
            "test",
            "tests",
            "pytest",
            "unittest",
        },
        "data_structures_algorithms": {
            "data structures",
            "algorithms",
            "algorithm",
            "stl",
        },
        "system_design": {
            "system design",
            "architecture",
        },
        "api_development": {
            "api",
            "apis",
            "api development",
            "rest api",
            "rest apis",
        },
        "python": {"python"},
    }

    def align(
        self,
        requirements: list[JobRequirement] | tuple[JobRequirement, ...],
        skill_matches: list[SkillMatch] | tuple[SkillMatch, ...],
        resume_skills: list[Skill] | tuple[Skill, ...],
        job_skills: list[Skill] | tuple[Skill, ...],
        structured_resume: StructuredResume,
    ) -> list[RequirementAlignment]:
        job_skill_by_id = {
            skill.skill_id: skill for skill in job_skills
        }

        alignments: list[RequirementAlignment] = []

        for requirement in requirements:
            if requirement.category == JobRequirementCategory.SKILL:
                alignment = self._align_skill_requirement(
                    requirement=requirement,
                    skill_matches=skill_matches,
                    job_skill_by_id=job_skill_by_id,
                )
            else:
                alignment = self._align_structured_requirement(
                    requirement=requirement,
                    structured_resume=structured_resume,
                )

            alignments.append(alignment)

        return alignments

    def _align_skill_requirement(
        self,
        *,
        requirement: JobRequirement,
        skill_matches: list[SkillMatch] | tuple[SkillMatch, ...],
        job_skill_by_id: dict[str, Skill],
    ) -> RequirementAlignment:
        mentioned_job_skills = [
            skill
            for skill in job_skill_by_id.values()
            if self._requirement_mentions_skill(requirement.text, skill)
        ]

        if not mentioned_job_skills:
            return RequirementAlignment(
                requirement_id=requirement.requirement_id,
                status=RequirementMatchStatus.UNKNOWN,
                confidence=requirement.confidence,
                rationale="no_matching_job_skill",
                evidence=requirement.evidence,
            )

        positive_matches: list[SkillMatch] = []
        missing_skill_count = 0

        for job_skill in mentioned_job_skills:
            matches_for_skill = [
                match
                for match in skill_matches
                if match.job_skill_id == job_skill.skill_id
            ]

            if not matches_for_skill:
                missing_skill_count += 1
                continue

            strongest_for_skill = max(
                matches_for_skill,
                key=lambda match: (
                    self._relationship_rank(match.relationship.value),
                    match.similarity,
                ),
            )

            if strongest_for_skill.relationship.value in {
                "exact",
                "strong_semantic",
                "partial",
            }:
                positive_matches.append(strongest_for_skill)
            else:
                missing_skill_count += 1

        if not positive_matches:
            return RequirementAlignment(
                requirement_id=requirement.requirement_id,
                status=RequirementMatchStatus.UNMATCHED,
                confidence=requirement.confidence,
                rationale="no_positive_skill_match",
                evidence=requirement.evidence,
            )

        relationships = [
            match.relationship.value
            for match in positive_matches
        ]

        if missing_skill_count > 0:
            status = RequirementMatchStatus.PARTIAL
        elif all(
            relationship in {"exact", "strong_semantic"}
            for relationship in relationships
        ):
            status = RequirementMatchStatus.MATCHED
        else:
            status = RequirementMatchStatus.PARTIAL

        strongest = max(
            positive_matches,
            key=lambda match: (
                self._relationship_rank(match.relationship.value),
                match.similarity,
            ),
        )

        evidence = list(requirement.evidence)
        for match in positive_matches:
            evidence.extend(match.evidence)

        return RequirementAlignment(
            requirement_id=requirement.requirement_id,
            status=status,
            confidence=strongest.confidence,
            rationale=(
                "aligned_via_compound_skills"
                if len(mentioned_job_skills) > 1
                else f"aligned_via_{strongest.relationship.value}"
            ),
            evidence=self._deduplicate_evidence(evidence),
        )

    def _align_structured_requirement(
        self,
        *,
        requirement: JobRequirement,
        structured_resume: StructuredResume,
    ) -> RequirementAlignment:
        if requirement.category == JobRequirementCategory.EXPERIENCE:
            return self._align_experience_requirement(
                requirement=requirement,
                structured_resume=structured_resume,
            )

        section_types = {
            JobRequirementCategory.EDUCATION: (
                ResumeSectionType.EDUCATION,
            ),
            JobRequirementCategory.CERTIFICATION: (
                ResumeSectionType.CERTIFICATIONS,
            ),
        }.get(requirement.category, ())

        if not section_types:
            return RequirementAlignment(
                requirement_id=requirement.requirement_id,
                status=RequirementMatchStatus.UNKNOWN,
                evidence=requirement.evidence,
                confidence=requirement.confidence,
                rationale="Requirement category has no supported structured resume evidence source.",
            )

        resume_blocks = []

        for section_type in section_types:
            for section in structured_resume.sections_of(section_type):
                resume_blocks.extend(section.blocks)

        if not resume_blocks:
            return RequirementAlignment(
                requirement_id=requirement.requirement_id,
                status=RequirementMatchStatus.UNKNOWN,
                evidence=requirement.evidence,
                confidence=requirement.confidence,
                rationale="No resume evidence was found for the required category.",
            )

        requirement_terms = self._meaningful_terms(requirement.text)
        matching_blocks = [
            block
            for block in resume_blocks
            if self._has_term_overlap(requirement_terms, block.text)
        ]

        if not matching_blocks:
            return RequirementAlignment(
                requirement_id=requirement.requirement_id,
                status=RequirementMatchStatus.UNKNOWN,
                evidence=requirement.evidence,
                confidence=requirement.confidence,
                rationale="Relevant resume section exists, but the requirement cannot be confirmed from available evidence.",
            )

        resume_evidence = [
            Evidence(
                evidence_id=(
                    f"resume-requirement-{requirement.requirement_id}-"
                    f"{index}"
                ),
                source_type=EvidenceSourceType.RESUME,
                source_document_id=structured_resume.document_id,
                section=section_name,
                text=block.text,
                start_offset=None,
                end_offset=None,
                evidence_type="requirement_alignment",
                extractor=self.ENGINE_VERSION,
                relevance=0.80,
                confidence=0.75,
            )
            for index, (block, section_name) in enumerate(
                self._blocks_with_sections(
                    structured_resume,
                    section_types,
                )
            )
            if block in matching_blocks
        ]

        evidence = self._deduplicate_evidence(
            list(requirement.evidence) + resume_evidence
        )

        overlap_ratio = self._best_overlap_ratio(
            requirement_terms,
            [block.text for block in matching_blocks],
        )

        if overlap_ratio >= 0.60:
            status = RequirementMatchStatus.MATCHED
        else:
            status = RequirementMatchStatus.PARTIAL

        return RequirementAlignment(
            requirement_id=requirement.requirement_id,
            status=status,
            evidence=evidence,
            confidence=requirement.confidence,
            rationale="structured_resume_evidence_found",
        )

    def _align_experience_requirement(
        self,
        *,
        requirement: JobRequirement,
        structured_resume: StructuredResume,
    ) -> RequirementAlignment:
        """
        Align an experience requirement using concept coverage across
        EXPERIENCE, PROJECTS, and SKILLS sections.

        Concept coverage is derived from an alias map so that synonymous
        terms (e.g. "etl" and "elt", "sql" and "postgresql") contribute to
        the same concept. A requirement is only MATCHED when every derived
        concept is evidenced somewhere in the resume. Partial coverage
        yields PARTIAL. No concept evidence yields UNKNOWN.
        """
        section_blocks: list[tuple[ResumeSectionType, str, object]] = []

        for section_type in self._EXPERIENCE_EVIDENCE_SECTIONS:
            for section in structured_resume.sections_of(section_type):
                heading = section.heading or section.section_type.value
                for block in section.blocks:
                    section_blocks.append(
                        (section_type, heading, block)
                    )

        requirement_concepts = self._derive_experience_concepts(
            requirement.text
        )

        if not requirement_concepts:
            return RequirementAlignment(
                requirement_id=requirement.requirement_id,
                status=RequirementMatchStatus.UNKNOWN,
                confidence=requirement.confidence,
                rationale="no_experience_concepts_derived",
                evidence=requirement.evidence,
            )

        if not section_blocks:
            return RequirementAlignment(
                requirement_id=requirement.requirement_id,
                status=RequirementMatchStatus.UNKNOWN,
                confidence=requirement.confidence,
                rationale="no_resume_evidence_found",
                evidence=requirement.evidence,
            )

        concept_evidence: dict[str, list[tuple[ResumeSectionType, str, object]]] = {
            concept: [] for concept in requirement_concepts
        }

        for section_type, heading, block in section_blocks:
            block_concepts = self._concepts_in_text(block.text)
            for concept in requirement_concepts:
                if concept in block_concepts:
                    concept_evidence[concept].append(
                        (section_type, heading, block)
                    )

        evidenced_concepts = [
            concept
            for concept, matches in concept_evidence.items()
            if matches
        ]

        if not evidenced_concepts:
            return RequirementAlignment(
                requirement_id=requirement.requirement_id,
                status=RequirementMatchStatus.UNKNOWN,
                confidence=requirement.confidence,
                rationale="no_resume_evidence_found",
                evidence=requirement.evidence,
            )

        covered_section_types: set[ResumeSectionType] = set()
        for concept in evidenced_concepts:
            for section_type, _, _ in concept_evidence[concept]:
                covered_section_types.add(section_type)

        all_evidenced = len(evidenced_concepts) == len(requirement_concepts)
        status = (
            RequirementMatchStatus.MATCHED
            if all_evidenced
            else RequirementMatchStatus.PARTIAL
        )

        resume_evidence: list[Evidence] = []
        seen_block_ids: set[int] = set()

        for index, concept in enumerate(evidenced_concepts):
            for section_type, heading, block in concept_evidence[concept]:
                if id(block) in seen_block_ids:
                    continue

                seen_block_ids.add(id(block))
                resume_evidence.append(
                    Evidence(
                        evidence_id=(
                            f"resume-experience-{requirement.requirement_id}-"
                            f"{index}-{len(resume_evidence)}"
                        ),
                        source_type=EvidenceSourceType.RESUME,
                        source_document_id=structured_resume.document_id,
                        section=heading,
                        text=block.text,
                        start_offset=None,
                        end_offset=None,
                        evidence_type="requirement_alignment",
                        extractor=self.ENGINE_VERSION,
                        relevance=0.80,
                        confidence=0.75,
                    )
                )

        professional_evidence = (
            ResumeSectionType.EXPERIENCE in covered_section_types
        )
        project_evidence = (
            ResumeSectionType.PROJECTS in covered_section_types
        )
        declared_skill_evidence = (
            ResumeSectionType.SKILLS in covered_section_types
        )

        if professional_evidence:
            rationale = "professional_experience_evidence_found"
        elif project_evidence and declared_skill_evidence:
            rationale = "mixed_resume_evidence_found"
        elif project_evidence:
            rationale = "project_experience_evidence_found"
        elif declared_skill_evidence:
            rationale = "declared_skill_evidence_found"
        else:
            rationale = "no_resume_evidence_found"

        evidence = self._deduplicate_evidence(
            list(requirement.evidence) + resume_evidence
        )

        return RequirementAlignment(
            requirement_id=requirement.requirement_id,
            status=status,
            confidence=requirement.confidence,
            rationale=rationale,
            evidence=evidence,
        )

    def _derive_experience_concepts(
        self,
        requirement_text: str,
    ) -> set[str]:
        """
        Map requirement text to the fixed set of experience concepts.

        A concept is derived when any of its aliases appears as a whole-word
        phrase inside the requirement text.
        """
        lowered = requirement_text.lower()
        concepts: set[str] = set()

        for concept, aliases in self._EXPERIENCE_CONCEPT_ALIASES.items():
            if self._contains_any_alias(lowered, aliases):
                concepts.add(concept)

        return concepts

    def _concepts_in_text(self, text: str) -> set[str]:
        """
        Return the experience concepts evidenced by a single resume block.

        Uses the same alias map as requirement-side derivation so coverage
        is symmetric.
        """
        lowered = text.lower()
        concepts: set[str] = set()

        for concept, aliases in self._EXPERIENCE_CONCEPT_ALIASES.items():
            if self._contains_any_alias(lowered, aliases):
                concepts.add(concept)

        return concepts

    @staticmethod
    def _contains_any_alias(
        lowered_text: str,
        aliases: set[str],
    ) -> bool:
        """
        Match each alias as a whole word or phrase.

        Aliases with punctuation (e.g. "etl/elt") are matched literally
        after the boundary check on the surrounding characters.
        """
        for alias in aliases:
            if not alias:
                continue

            if re.search(
                rf"(?<!\w){re.escape(alias)}(?!\w)",
                lowered_text,
            ):
                return True

        return False

    @staticmethod
    def _requirement_mentions_skill(
        requirement_text: str,
        skill: Skill,
    ) -> bool:
        text = requirement_text.lower()
        candidates = {
            skill.canonical_name.lower(),
            skill.display_name.lower(),
            *(alias.lower() for alias in skill.aliases),
        }

        return any(
            re.search(
                rf"(?<!\w){re.escape(candidate)}(?!\w)",
                text,
            )
            for candidate in candidates
            if candidate
        )

    @staticmethod
    def _skill_match_status(relationship: str) -> RequirementMatchStatus:
        if relationship in {"exact", "strong_semantic"}:
            return RequirementMatchStatus.MATCHED

        if relationship in {"partial", "related"}:
            return RequirementMatchStatus.PARTIAL

        return RequirementMatchStatus.UNMATCHED

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
    def _meaningful_terms(text: str) -> set[str]:
        tokens = re.findall(r"[a-zA-Z0-9+#.]+", text.lower())
        stop_words = {
            "and",
            "or",
            "the",
            "a",
            "an",
            "of",
            "to",
            "with",
            "in",
            "for",
            "on",
            "is",
            "are",
            "years",
            "year",
            "experience",
            "required",
            "preferred",
            "qualification",
            "qualifications",
            "degree",
            "certification",
            "certified",
        }
        return {
            token
            for token in tokens
            if token not in stop_words and len(token) > 1
        }

    @classmethod
    def _has_term_overlap(
        cls,
        requirement_terms: set[str],
        resume_text: str,
    ) -> bool:
        resume_terms = cls._meaningful_terms(resume_text)
        return bool(requirement_terms & resume_terms)

    @classmethod
    def _best_overlap_ratio(
        cls,
        requirement_terms: set[str],
        resume_texts: list[str],
    ) -> float:
        if not requirement_terms:
            return 0.0

        best = 0.0

        for text in resume_texts:
            resume_terms = cls._meaningful_terms(text)
            overlap = requirement_terms & resume_terms
            ratio = len(overlap) / len(requirement_terms)
            best = max(best, ratio)

        return best

    @staticmethod
    def _blocks_with_sections(
        structured_resume: StructuredResume,
        section_types: tuple[ResumeSectionType, ...],
    ):
        for section in structured_resume.sections:
            if section.section_type not in section_types:
                continue

            for block in section.blocks:
                yield block, section.heading or section.section_type.value

    @staticmethod
    def _deduplicate_evidence(
        evidence: list[Evidence],
    ) -> list[Evidence]:
        seen: set[str] = set()
        result: list[Evidence] = []

        for item in evidence:
            if item.evidence_id in seen:
                continue

            seen.add(item.evidence_id)
            result.append(item)

        return result