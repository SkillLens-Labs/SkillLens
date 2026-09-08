from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    ParsedDocument,
)


class JDSectionType(StrEnum):
    """Semantic section types commonly found in job descriptions."""

    HEADER = "header"
    SUMMARY = "summary"
    RESPONSIBILITIES = "responsibilities"
    REQUIRED_QUALIFICATIONS = "required_qualifications"
    PREFERRED_QUALIFICATIONS = "preferred_qualifications"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class JDSection:
    """A semantically interpreted section of a job description."""

    section_type: JDSectionType
    heading: str | None
    blocks: tuple[DocumentBlock, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StructuredJobDescription:
    """Job-description structure interpreted from a ParsedDocument."""

    document_id: str
    sections: tuple[JDSection, ...] = field(default_factory=tuple)

    def sections_of(
        self,
        section_type: JDSectionType,
    ) -> tuple[JDSection, ...]:
        """Return all sections matching the requested semantic type."""

        return tuple(
            section
            for section in self.sections
            if section.section_type == section_type
        )


class JDStructureInterpreter:
    """Interpret structural job-description sections from a ParsedDocument."""

    _SECTION_ALIASES: dict[JDSectionType, frozenset[str]] = {
        JDSectionType.SUMMARY: frozenset(
            {
                "summary",
                "job summary",
                "position summary",
                "role summary",
                "about the role",
                "about this role",
                "overview",
                "job overview",
                "position overview",
            }
        ),
        JDSectionType.RESPONSIBILITIES: frozenset(
            {
                "responsibilities",
                "key responsibilities",
                "roles and responsibilities",
                "role and responsibilities",
                "duties",
                "job duties",
                "what you'll do",
                "what you will do",
                "what you'll be doing",
                "what you will be doing",
            }
        ),
        JDSectionType.REQUIRED_QUALIFICATIONS: frozenset(
            {
                "requirements",
                "required qualifications",
                "minimum qualifications",
                "basic qualifications",
                "must have",
                "required skills",
                "required experience",
                "qualifications",
            }
        ),
        JDSectionType.PREFERRED_QUALIFICATIONS: frozenset(
            {
                "preferred qualifications",
                "preferred requirements",
                "preferred skills",
                "preferred experience",
                "nice to have",
                "nice-to-have",
                "desired qualifications",
                "additional qualifications",
            }
        ),
        JDSectionType.SKILLS: frozenset(
            {
                "skills",
                "technical skills",
                "required skills",
                "technical requirements",
                "technologies",
                "technology",
                "tech stack",
                "technical competencies",
            }
        ),
        JDSectionType.EXPERIENCE: frozenset(
            {
                "experience",
                "required experience",
                "professional experience",
                "work experience",
                "years of experience",
            }
        ),
        JDSectionType.EDUCATION: frozenset(
            {
                "education",
                "educational requirements",
                "educational qualifications",
                "academic requirements",
                "academic qualifications",
                "degree requirements",
            }
        ),
        JDSectionType.CERTIFICATIONS: frozenset(
            {
                "certifications",
                "certification requirements",
                "licenses",
                "licenses and certifications",
                "licenses & certifications",
            }
        ),
    }

    def interpret(
        self,
        document: ParsedDocument,
    ) -> StructuredJobDescription:
        """Interpret a parsed job description without reparsing the source."""

        sections: list[JDSection] = []
        current_type = JDSectionType.HEADER
        current_heading: str | None = None
        current_blocks: list[DocumentBlock] = []

        for block in document.blocks:
            heading_type = self._classify_heading(block)

            if heading_type is not None:
                if current_blocks or current_heading is not None:
                    sections.append(
                        JDSection(
                            section_type=current_type,
                            heading=current_heading,
                            blocks=tuple(current_blocks),
                        )
                    )

                current_type = heading_type
                current_heading = block.text.strip()
                current_blocks = []
                continue

            current_blocks.append(block)

        if current_blocks or current_heading is not None:
            sections.append(
                JDSection(
                    section_type=current_type,
                    heading=current_heading,
                    blocks=tuple(current_blocks),
                )
            )

        return StructuredJobDescription(
            document_id=document.document_id,
            sections=tuple(sections),
        )

    def _classify_heading(
        self,
        block: DocumentBlock,
    ) -> JDSectionType | None:
        """Return a semantic section type when a block is a JD heading."""

        if block.block_type != DocumentBlockType.HEADING:
            return None

        normalized = self._normalize_heading(block.text)

        for section_type, aliases in self._SECTION_ALIASES.items():
            if normalized in aliases:
                return section_type

        return JDSectionType.UNKNOWN

    @staticmethod
    def _normalize_heading(text: str) -> str:
        """Normalize heading text for alias matching."""

        normalized = " ".join(text.strip().lower().split())
        normalized = normalized.rstrip(":")
        return normalized