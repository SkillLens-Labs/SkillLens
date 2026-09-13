from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256

from backend.app.analysis.jd_structure import (
    JDSection,
    JDSectionType,
    StructuredJobDescription,
)
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.matching import (
    JobRequirement,
    JobRequirementCategory,
    JobRequirementType,
)


@dataclass(frozen=True)
class _RequirementCandidate:
    text: str
    section: JDSection
    block_index: int


class JDRequirementExtractor:
    """
    Extract structured requirements from an interpreted job description.

    This component is intentionally limited to JD-side requirement extraction.
    It does not perform normalization, ESCO mapping, matching, scoring, or XAI.
    """

    _REQUIRED_SECTIONS = frozenset(
        {
            JDSectionType.REQUIRED_QUALIFICATIONS,
            JDSectionType.EXPERIENCE,
            JDSectionType.EDUCATION,
            JDSectionType.CERTIFICATIONS,
        }
    )

    _PREFERRED_SECTIONS = frozenset(
        {
            JDSectionType.PREFERRED_QUALIFICATIONS,
        }
    )


    _EXPERIENCE_PATTERNS = (
        re.compile(r"\b\d+(?:\.\d+)?\+?\s*(?:years?|yrs?)\b", re.IGNORECASE),
        re.compile(r"\bminimum\s+\d+(?:\.\d+)?\s*(?:years?|yrs?)\b", re.IGNORECASE),
        re.compile(r"\bat least\s+\d+(?:\.\d+)?\s*(?:years?|yrs?)\b", re.IGNORECASE),
        re.compile(r"\bexperience\s+(?:with|in|of)\b", re.IGNORECASE),
    )

    _EDUCATION_TERMS = (
        "bachelor",
        "bachelors",
        "bachelor's",
        "master",
        "masters",
        "master's",
        "degree",
        "b.e.",
        "b.tech",
        "btech",
        "m.e.",
        "m.tech",
        "mtech",
        "phd",
        "doctorate",
        "diploma",
    )

    _CERTIFICATION_TERMS = (
        "certification",
        "certified",
        "certificate",
        "license",
        "licensed",
    )

    def extract(
        self,
        document: StructuredJobDescription,
    ) -> list[JobRequirement]:
        """
        Extract requirements while preserving source order and evidence.

        Requirements are generated only from explicit requirement-oriented
        sections or explicit requirement language. Unknown content is not
        promoted into a requirement.
        """
        candidates: list[_RequirementCandidate] = []

        for section in document.sections:
            requirement_type = self._requirement_type_for_section(section.section_type)
            if requirement_type is None:
                continue

            for block_index, block in enumerate(section.blocks):
                text = self._clean_text(block.text)
                if not text:
                    continue

                for item in self._split_requirement_text(text):
                    item = self._clean_text(item)
                    if not item:
                        continue

                    candidates.append(
                        _RequirementCandidate(
                            text=item,
                            section=section,
                            block_index=block_index,
                        )
                    )

        requirements: list[JobRequirement] = []

        for candidate in candidates:
            requirement_type = self._requirement_type_for_candidate(
                section_type=candidate.section.section_type,
                text=candidate.text,
            )
            if requirement_type is None:
                continue

            category = self._classify_category(
                candidate.text,
                candidate.section.section_type,
            )

            requirements.append(
                self._build_requirement(
                    candidate=candidate,
                    requirement_type=requirement_type,
                    category=category,
                    document_id=document.document_id,
                    sequence=len(requirements),
                )
            )

        return requirements

    def _build_requirement(
        self,
        *,
        candidate: _RequirementCandidate,
        requirement_type: JobRequirementType,
        category: JobRequirementCategory,
        document_id: str,
        sequence: int,
    ) -> JobRequirement:
        requirement_id = self._requirement_id(
            document_id=document_id,
            sequence=sequence,
            text=candidate.text,
            category=category,
            requirement_type=requirement_type,
        )

        evidence = Evidence(
            evidence_id=f"{requirement_id}:evidence",
            source_type=EvidenceSourceType.JOB_DESCRIPTION,
            source_document_id=document_id,
            section=candidate.section.section_type.value,
            text=candidate.text,
            evidence_type="job_requirement",
            extractor="jd_requirement_extractor",
            relevance=1.0,
            confidence=0.95,
        )

        confidence = Confidence(
            score=0.95,
            level=ConfidenceLevel.HIGH,
            components={
                "section_signal": 1.0,
                "requirement_signal": 0.9,
            },
            rationale=(
                "Requirement extracted from an explicit job-description "
                "qualification or requirement section."
            ),
        )

        return JobRequirement(
            requirement_id=requirement_id,
            text=candidate.text,
            requirement_type=requirement_type,
            category=category,
            evidence=[evidence],
            confidence=confidence,
            metadata={
                "source_block_index": candidate.block_index,
                "source_heading": candidate.section.heading,
            },
        )

    @classmethod
    def _classify_category(
        cls,
        text: str,
        section_type: JDSectionType,
    ) -> JobRequirementCategory:
        normalized = text.lower()

        if section_type == JDSectionType.EDUCATION:
            return JobRequirementCategory.EDUCATION

        if section_type == JDSectionType.CERTIFICATIONS:
            return JobRequirementCategory.CERTIFICATION

        if section_type == JDSectionType.EXPERIENCE:
            return JobRequirementCategory.EXPERIENCE

        if cls._looks_like_education(normalized):
            return JobRequirementCategory.EDUCATION

        if cls._looks_like_certification(normalized):
            return JobRequirementCategory.CERTIFICATION

        if cls._looks_like_experience(normalized):
            return JobRequirementCategory.EXPERIENCE

        return JobRequirementCategory.SKILL

    @classmethod
    def _looks_like_experience(cls, text: str) -> bool:
        return any(pattern.search(text) for pattern in cls._EXPERIENCE_PATTERNS)

    @classmethod
    def _looks_like_education(cls, text: str) -> bool:
        return any(term in text for term in cls._EDUCATION_TERMS)

    @classmethod
    def _looks_like_certification(cls, text: str) -> bool:
        return any(term in text for term in cls._CERTIFICATION_TERMS)

    @classmethod
    def _requirement_type_for_candidate(
        cls,
        *,
        section_type: JDSectionType,
        text: str,
    ) -> JobRequirementType | None:
        normalized = text.casefold()

        explicit_preferred = (
            re.search(r"\bpreferred\b", normalized) is not None
            or re.search(r"\bdesired\b", normalized) is not None
            or re.search(r"\bbonus\b", normalized) is not None
            or re.search(r"\bnice[- ]to[- ]have\b", normalized) is not None
            or re.search(r"\bis\s+a\s+plus\b", normalized) is not None
            or re.search(r"\bwould\s+be\s+a\s+plus\b", normalized) is not None
            or re.search(r"\badvantage\b", normalized) is not None
            or re.search(r"\bbeneficial\b", normalized) is not None
        )

        explicit_required = (
            re.search(r"\brequired\b", normalized) is not None
            or re.search(r"\bmust\b", normalized) is not None
            or re.search(r"\bmandatory\b", normalized) is not None
        )

        if explicit_preferred and not explicit_required:
            return JobRequirementType.PREFERRED

        if explicit_required:
            return JobRequirementType.REQUIRED

        return cls._requirement_type_for_section(section_type)

    @classmethod
    def _requirement_type_for_section(
        cls,
        section_type: JDSectionType,
    ) -> JobRequirementType | None:
        if section_type in cls._REQUIRED_SECTIONS:
            return JobRequirementType.REQUIRED

        if section_type in cls._PREFERRED_SECTIONS:
            return JobRequirementType.PREFERRED

        if section_type == JDSectionType.SKILLS:
            return JobRequirementType.REQUIRED

        return None

    @staticmethod
    def _split_requirement_text(text: str) -> list[str]:
        """
        Preserve bullets as individual requirements while avoiding aggressive
        sentence splitting that could destroy technical requirement text.
        """
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if len(lines) > 1:
            return lines

        return [text]

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"^[\s•●○▪▫‣*–—-]+", "", text.strip())
        return " ".join(text.split()).strip()

    @staticmethod
    def _requirement_id(
        *,
        document_id: str,
        sequence: int,
        text: str,
        category: JobRequirementCategory,
        requirement_type: JobRequirementType,
    ) -> str:
        payload = (
            f"{document_id}|{sequence}|{category.value}|"
            f"{requirement_type.value}|{text.lower()}"
        )
        digest = sha256(payload.encode("utf-8")).hexdigest()[:16]
        return f"req-{digest}"