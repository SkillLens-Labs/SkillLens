from __future__ import annotations

from dataclasses import dataclass, field
import re

from backend.app.analysis.resume_structure import (
    ResumeSectionType,
    StructuredResume,
)
from backend.app.infrastructure.parsers.models import DocumentBlock


class SkillEvidenceType:
    EXPLICIT = "explicit"
    CONTEXTUAL = "contextual"


@dataclass(frozen=True)
class SkillMention:
    """A candidate skill mention extracted from resume evidence."""

    raw_text: str
    section_type: ResumeSectionType
    evidence_type: str
    block: DocumentBlock
    start_offset: int
    end_offset: int
    extractor: str
    confidence: float
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class SkillExtractionResult:
    """All candidate skill mentions extracted from a structured resume."""

    document_id: str
    mentions: tuple[SkillMention, ...] = field(default_factory=tuple)


class SkillExtractor:
    """Extract candidate skill mentions from an interpreted resume."""

    _EXPLICIT_SECTIONS = frozenset(
        {
            ResumeSectionType.SKILLS,
            ResumeSectionType.CERTIFICATIONS,
        }
    )

    _CONTEXTUAL_SECTIONS = frozenset(
        {
            ResumeSectionType.SUMMARY,
            ResumeSectionType.EXPERIENCE,
            ResumeSectionType.PROJECTS,
            ResumeSectionType.EDUCATION,
        }
    )

    # Phase 3 extraction vocabulary.
    #
    # This is intentionally a candidate-detection vocabulary rather than
    # the canonical skill taxonomy. Normalization and ESCO mapping happen
    # in later Phase 3 steps.
    _KNOWN_SKILLS: tuple[str, ...] = (
        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
        "C++",
        "C#",
        "Go",
        "Rust",
        "SQL",
        "NoSQL",
        "HTML",
        "CSS",
        "React",
        "React.js",
        "Angular",
        "Vue.js",
        "Node.js",
        "FastAPI",
        "Django",
        "Flask",
        "Spring Boot",
        "REST API",
        "REST APIs",
        "GraphQL",
        "Git",
        "GitHub",
        "Docker",
        "Kubernetes",
        "AWS",
        "Azure",
        "GCP",
        "Linux",
        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Redis",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "scikit-learn",
        "TensorFlow",
        "PyTorch",
        "XGBoost",
        "Machine Learning",
        "Deep Learning",
        "Natural Language Processing",
        "NLP",
        "Transformers",
        "Hugging Face",
        "Data Analysis",
        "Data Science",
        "Statistics",
        "Power BI",
        "Tableau",
        "Excel",
    )

    _SKILL_PATTERN = re.compile(
        r"(?<!\w)("
        + "|".join(
            re.escape(skill)
            for skill in sorted(_KNOWN_SKILLS, key=len, reverse=True)
        )
        + r")(?!\w)",
        re.IGNORECASE,
    )

    def extract(self, resume: StructuredResume) -> SkillExtractionResult:
        """Extract candidate skills without normalizing or mapping them."""
        mentions: list[SkillMention] = []

        for section in resume.sections:
            if section.section_type not in (
                self._EXPLICIT_SECTIONS | self._CONTEXTUAL_SECTIONS
            ):
                continue

            evidence_type = (
                SkillEvidenceType.EXPLICIT
                if section.section_type in self._EXPLICIT_SECTIONS
                else SkillEvidenceType.CONTEXTUAL
            )

            for block in section.blocks:
                mentions.extend(
                    self._extract_from_block(
                        block=block,
                        section_type=section.section_type,
                        evidence_type=evidence_type,
                    )
                )

        return SkillExtractionResult(
            document_id=resume.document_id,
            mentions=tuple(mentions),
        )

    def _extract_from_block(
        self,
        *,
        block: DocumentBlock,
        section_type: ResumeSectionType,
        evidence_type: str,
    ) -> list[SkillMention]:
        """Extract known candidate skills from one document block."""
        mentions: list[SkillMention] = []

        for match in self._SKILL_PATTERN.finditer(block.text):
            raw_text = match.group(1)

            confidence = (
                0.95
                if evidence_type == SkillEvidenceType.EXPLICIT
                else 0.80
            )

            mentions.append(
                SkillMention(
                    raw_text=raw_text,
                    section_type=section_type,
                    evidence_type=evidence_type,
                    block=block,
                    start_offset=match.start(1),
                    end_offset=match.end(1),
                    extractor="deterministic_skill_lexicon",
                    confidence=confidence,
                )
            )

        return mentions