from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re

from backend.app.analysis.esco_mapper import ESCOMapResult
from backend.app.analysis.jd_structure import (
    JDSectionType,
    StructuredJobDescription,
)
from backend.app.analysis.skill_normalizer import NormalizedSkill
from backend.app.domain.job import (
    EducationRequirements,
    ExperienceRequirements,
    JobProfile,
)
from backend.app.domain.matching import (
    JobRequirement,
    JobRequirementCategory,
    JobRequirementType,
)
from backend.app.domain.skill import Skill


@dataclass(frozen=True)
class JDProfileBuildResult:
    """Internal Phase 5 build output shared by profile and matching stages."""

    profile: JobProfile
    skills: tuple[Skill, ...]
    requirements: tuple[JobRequirement, ...]


class JDProfileBuilder:
    """
    Build the canonical JobProfile from Phase 5 JD analysis outputs.

    This builder owns JD profile construction only. It does not perform
    resume matching, scoring, or XAI.
    """

    BUILDER_VERSION = "phase5-v1"
    ESCO_VERSION = "1.2.1"

    def build(
        self,
        document: StructuredJobDescription,
        requirements: tuple[JobRequirement, ...] | list[JobRequirement],
        normalized_skills: tuple[NormalizedSkill, ...] | list[NormalizedSkill],
        esco_results: tuple[ESCOMapResult, ...] | list[ESCOMapResult],
    ) -> JobProfile:
        """
        Construct one canonical JobProfile.

        normalized_skills and esco_results must remain positionally aligned.
        """
        result = self._build(
            document=document,
            requirements=requirements,
            normalized_skills=normalized_skills,
            esco_results=esco_results,
        )
        return result.profile

    def build_with_skills(
        self,
        document: StructuredJobDescription,
        requirements: tuple[JobRequirement, ...] | list[JobRequirement],
        normalized_skills: tuple[NormalizedSkill, ...] | list[NormalizedSkill],
        esco_results: tuple[ESCOMapResult, ...] | list[ESCOMapResult],
    ) -> JDProfileBuildResult:
        """Build the canonical JD profile and expose its canonical skills."""
        return self._build(
            document=document,
            requirements=requirements,
            normalized_skills=normalized_skills,
            esco_results=esco_results,
        )

    def _build(
        self,
        document: StructuredJobDescription,
        requirements: tuple[JobRequirement, ...] | list[JobRequirement],
        normalized_skills: tuple[NormalizedSkill, ...] | list[NormalizedSkill],
        esco_results: tuple[ESCOMapResult, ...] | list[ESCOMapResult],
    ) -> JDProfileBuildResult:
        """Build the profile and canonical JD skills through one path."""
        requirements = tuple(requirements)
        normalized_skills = tuple(normalized_skills)
        esco_results = tuple(esco_results)

        if len(normalized_skills) != len(esco_results):
            raise ValueError(
                "normalized_skills and esco_results must contain the same number "
                "of items"
            )

        skills = tuple(
            self._build_skills(
                document_id=document.document_id,
                normalized_skills=normalized_skills,
                esco_results=esco_results,
            )
        )

        required_skill_names = self._skill_names_for_requirements(
            requirements,
            JobRequirementType.REQUIRED,
        )
        preferred_skill_names = self._skill_names_for_requirements(
            requirements,
            JobRequirementType.PREFERRED,
        )

        if not required_skill_names:
            required_skill_names = self._skill_names_from_sections(
                normalized_skills,
                JobRequirementType.REQUIRED,
            )

        if not preferred_skill_names:
            preferred_skill_names = self._skill_names_from_sections(
                normalized_skills,
                JobRequirementType.PREFERRED,
            )

        profile = JobProfile(
            profile_id=self._profile_id(document.document_id),
            document_id=document.document_id,
            job_title=self._extract_job_title(document),
            company=self._extract_company(document),
            summary=self._extract_section_text(
                document,
                JDSectionType.SUMMARY,
            ),
            responsibilities=self._extract_section_lines(
                document,
                JDSectionType.RESPONSIBILITIES,
            ),
            required_skills=required_skill_names,
            preferred_skills=preferred_skill_names,
            technical_skills=[
                skill.canonical_name
                for skill in skills
                if skill.category in {
                    "programming",
                    "web",
                    "data",
                    "cloud_devops",
                    "tooling",
                }
            ],
            soft_skills=[],
            domain_skills=[],
            experience_requirements=self._build_experience_requirements(
                requirements,
            ),
            education_requirements=self._build_education_requirements(
                requirements,
            ),
            seniority=self._extract_seniority(document),
            metadata={
                "builder": self.__class__.__name__,
                "builder_version": self.BUILDER_VERSION,
                "esco_version": self.ESCO_VERSION,
                "skill_count": len(skills),
                "requirement_count": len(requirements),
                "required_skill_count": len(required_skill_names),
                "preferred_skill_count": len(preferred_skill_names),
                "requirements": [
                    requirement.model_dump(mode="json")
                    for requirement in requirements
                ],
            },
        )

        return JDProfileBuildResult(
            profile=profile,
            skills=skills,
            requirements=requirements,
        )

    def _build_skills(
        self,
        *,
        document_id: str,
        normalized_skills: tuple[NormalizedSkill, ...],
        esco_results: tuple[ESCOMapResult, ...],
    ) -> list[Skill]:
        skills: list[Skill] = []
        seen: set[str] = set()

        for normalized_skill, esco_result in zip(
            normalized_skills,
            esco_results,
            strict=True,
        ):
            skill_id = self._skill_id(
                document_id,
                normalized_skill.canonical_name,
            )

            if skill_id in seen:
                continue

            seen.add(skill_id)

            display_name = (
                esco_result.candidates[0].preferred_label
                if esco_result.candidates
                else normalized_skill.canonical_name
            )

            skills.append(
                Skill(
                    skill_id=skill_id,
                    canonical_name=normalized_skill.canonical_name,
                    display_name=display_name,
                    category=self._skill_category(
                        normalized_skill.canonical_name,
                    ),
                    aliases=self._aliases(normalized_skill),
                    metadata={
                        "source": "job_description",
                        "source_section": normalized_skill.metadata.get(
                            "jd_section_type",
                        ),
                        "source_evidence_type": normalized_skill.mention.evidence_type,
                        "normalization_method": normalized_skill.metadata.get(
                            "normalization_method",
                        ),
                        "esco_status": esco_result.status.value,
                        "esco_version": esco_result.esco_version,
                        "esco_mapping_method": esco_result.mapping_method,
                        **self._esco_metadata(esco_result),
                    },
                )
            )

        return skills

    @staticmethod
    def _esco_metadata(
        esco_result: ESCOMapResult,
    ) -> dict[str, object]:
        if not esco_result.candidates:
            return {}

        metadata: dict[str, object] = {
            "esco_preferred_label": (
                esco_result.candidates[0].preferred_label
            ),
        }

        if esco_result.candidates[0].uri:
            metadata["esco_uri"] = esco_result.candidates[0].uri

        return metadata

    @staticmethod
    def _skill_names_for_requirements(
        requirements: tuple[JobRequirement, ...],
        requirement_type: JobRequirementType,
    ) -> list[str]:
        names: list[str] = []
        seen: set[str] = set()

        for requirement in requirements:
            if requirement.requirement_type != requirement_type:
                continue
            if requirement.category != JobRequirementCategory.SKILL:
                continue
            if not requirement.canonical_name:
                continue

            name = requirement.canonical_name
            if name in seen:
                continue

            seen.add(name)
            names.append(name)

        return names

    @staticmethod
    def _skill_names_from_sections(
        normalized_skills: tuple[NormalizedSkill, ...],
        requirement_type: JobRequirementType,
    ) -> list[str]:
        allowed_sections = (
            {
                JDSectionType.SKILLS,
                JDSectionType.REQUIRED_QUALIFICATIONS,
            }
            if requirement_type == JobRequirementType.REQUIRED
            else {JDSectionType.PREFERRED_QUALIFICATIONS}
        )

        names: list[str] = []
        seen: set[str] = set()

        for normalized_skill in normalized_skills:
            section_type = normalized_skill.metadata.get("jd_section_type")

            if section_type not in {section.value for section in allowed_sections}:
                continue

            name = normalized_skill.canonical_name

            if name in seen:
                continue

            seen.add(name)
            names.append(name)

        return names

    @staticmethod
    def _build_experience_requirements(
        requirements: tuple[JobRequirement, ...],
    ) -> ExperienceRequirements | None:
        experience_requirements = [
            requirement
            for requirement in requirements
            if requirement.category is JobRequirementCategory.EXPERIENCE
        ]

        descriptions = [
            requirement.text.strip()
            for requirement in experience_requirements
            if requirement.text.strip()
        ]

        combined_text = " ".join(descriptions)

        range_match = re.search(
            r"\b(\d+(?:\.\d+)?)\s*(?:[-–—]|to)\s*"
            r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
            combined_text,
            flags=re.IGNORECASE,
        )

        plus_match = re.search(
            r"\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b",
            combined_text,
            flags=re.IGNORECASE,
        )

        minimum_years: float | None = None
        maximum_years: float | None = None

        if range_match:
            minimum_years = float(range_match.group(1))
            maximum_years = float(range_match.group(2))
        elif plus_match:
            minimum_years = float(plus_match.group(1))

        if not descriptions:
            return None

        return ExperienceRequirements(
            minimum_years=minimum_years,
            maximum_years=maximum_years,
            description=" ".join(descriptions),
        )

    @staticmethod
    def _build_education_requirements(
        requirements: tuple[JobRequirement, ...],
    ) -> EducationRequirements | None:
        education_requirements = [
            requirement
            for requirement in requirements
            if requirement.category is JobRequirementCategory.EDUCATION
        ]

        if not education_requirements:
            return None

        descriptions = [
            requirement.text.strip()
            for requirement in education_requirements
            if requirement.text.strip()
        ]

        combined_text = " ".join(descriptions)
        normalized = combined_text.casefold()

        degrees: list[str] = []

        degree_aliases = (
            ("bachelor", "bachelor"),
            ("b.e.", "bachelor"),
            ("b.tech", "bachelor"),
            ("b.sc", "bachelor"),
            ("master", "master"),
            ("m.e.", "master"),
            ("m.tech", "master"),
            ("m.sc", "master"),
            ("phd", "phd"),
            ("doctorate", "phd"),
        )

        for alias, canonical in degree_aliases:
            if alias in normalized and canonical not in degrees:
                degrees.append(canonical)

        fields_of_study: list[str] = []

        field_match = re.search(
            r"\b(?:in|with\s+(?:a\s+)?(?:degree|background)\s+in)\s+"
            r"(.+?)(?:\.|$)",
            combined_text,
            flags=re.IGNORECASE,
        )

        if field_match:
            field_text = field_match.group(1).strip()

            field_text = re.sub(
                r"\s+or\s+related\s+field.*$",
                "",
                field_text,
                flags=re.IGNORECASE,
            )

            for field in re.split(r",|\bor\b", field_text, flags=re.IGNORECASE):
                field = field.strip(" .")
                if field and field.casefold() not in {
                    existing.casefold() for existing in fields_of_study
                }:
                    fields_of_study.append(field)

        return EducationRequirements(
            degrees=degrees,
            fields_of_study=fields_of_study,
            description=combined_text or None,
        )

    @staticmethod
    def _extract_section_text(
        document: StructuredJobDescription,
        section_type: JDSectionType,
    ) -> str | None:
        sections = document.sections_of(section_type)

        for section in sections:
            texts = [
                block.text.strip()
                for block in section.blocks
                if block.text.strip()
            ]
            if texts:
                return "\n".join(texts)

        return None

    @staticmethod
    def _extract_section_lines(
        document: StructuredJobDescription,
        section_type: JDSectionType,
    ) -> list[str]:
        sections = document.sections_of(section_type)
        lines: list[str] = []

        for section in sections:
            for block in section.blocks:
                text = block.text.strip()
                if text:
                    lines.append(text)

        return lines

    @staticmethod
    def _extract_job_title(
        document: StructuredJobDescription,
    ) -> str:
        header_sections = document.sections_of(JDSectionType.HEADER)

        # The HEADER heading represents the document/job title when present.
        for section in header_sections:
            if section.heading and section.heading.strip():
                return section.heading.strip()

        # Fall back to a non-metadata header block when no header heading exists.
        metadata_prefixes = (
            "company:",
            "location:",
            "employment type:",
            "experience:",
        )

        for section in header_sections:
            for block in section.blocks:
                text = block.text.strip()
                if not text:
                    continue

                normalized = text.casefold()
                if normalized.startswith(metadata_prefixes):
                    continue

                return text

        for section in document.sections:
            if section.heading:
                return section.heading.strip()

        return "Unknown"

    @staticmethod
    def _extract_company(
        document: StructuredJobDescription,
    ) -> str | None:
        """Extract company name from explicit header metadata or header text."""
        for section in document.sections_of(JDSectionType.HEADER):
            for block in section.blocks:
                metadata_company = block.metadata.get("company")
                if metadata_company:
                    return str(metadata_company).strip() or None

                match = re.match(
                    r"^\s*company\s*:\s*(.+?)\s*$",
                    block.text,
                    flags=re.IGNORECASE,
                )
                if match:
                    return match.group(1).strip() or None

        return None

    @staticmethod
    def _extract_seniority(
        document: StructuredJobDescription,
    ) -> str | None:
        text = " ".join(
            block.text.lower()
            for section in document.sections
            for block in section.blocks
        )

        seniority_terms = (
            "intern",
            "junior",
            "entry level",
            "associate",
            "mid level",
            "mid-level",
            "senior",
            "lead",
            "principal",
            "staff",
            "manager",
            "director",
        )

        for term in seniority_terms:
            if term in text:
                return term

        return None

    @staticmethod
    def _skill_category(
        canonical_name: str,
    ) -> str | None:
        programming = {
            "python",
            "java",
            "javascript",
            "typescript",
            "c++",
            "c#",
            "go",
            "rust",
        }

        web = {
            "html",
            "css",
            "react",
            "angular",
            "vue.js",
            "node.js",
            "fastapi",
            "django",
            "flask",
            "spring boot",
            "rest api",
            "graphql",
        }

        data = {
            "sql",
            "nosql",
            "postgresql",
            "mysql",
            "mongodb",
            "redis",
            "pandas",
            "numpy",
            "scikit-learn",
            "machine learning",
            "deep learning",
            "natural language processing",
            "transformers",
            "data analysis",
            "data science",
            "statistics",
            "power bi",
            "tableau",
            "excel",
        }

        cloud_devops = {
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "linux",
        }

        tooling = {
            "git",
            "github",
        }

        if canonical_name in programming:
            return "programming"
        if canonical_name in web:
            return "web"
        if canonical_name in data:
            return "data"
        if canonical_name in cloud_devops:
            return "cloud_devops"
        if canonical_name in tooling:
            return "tooling"

        return None

    @staticmethod
    def _aliases(
        normalized_skill: NormalizedSkill,
    ) -> list[str]:
        aliases: list[str] = []

        if normalized_skill.raw_text.lower() != normalized_skill.canonical_name:
            aliases.append(normalized_skill.raw_text)

        if (
            normalized_skill.matched_alias
            and normalized_skill.matched_alias not in aliases
        ):
            aliases.append(normalized_skill.matched_alias)

        return aliases

    @staticmethod
    def _profile_id(document_id: str) -> str:
        digest = sha256(
            f"job-profile|{document_id}".encode("utf-8")
        ).hexdigest()[:16]

        return f"job_{digest}"

    @staticmethod
    def _skill_id(
        document_id: str,
        canonical_name: str,
    ) -> str:
        digest = sha256(
            f"{document_id}|{canonical_name}".encode("utf-8")
        ).hexdigest()[:16]

        return f"job-skill-{digest}"