from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    ParsedDocument,
)


class ResumeSectionType(StrEnum):
    HEADER = "header"
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    SKILLS = "skills"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ResumeSection:
    """A semantically interpreted section of a resume."""

    section_type: ResumeSectionType
    heading: str | None
    blocks: tuple[DocumentBlock, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StructuredResume:
    """Resume structure interpreted from a ParsedDocument."""

    document_id: str
    sections: tuple[ResumeSection, ...] = field(default_factory=tuple)

    def sections_of(
        self,
        section_type: ResumeSectionType,
    ) -> tuple[ResumeSection, ...]:
        """Return all sections matching the requested semantic type."""
        return tuple(
            section
            for section in self.sections
            if section.section_type == section_type
        )


class ResumeStructureInterpreter:
    """Interpret structural resume sections from a ParsedDocument."""

    _SECTION_ALIASES: dict[ResumeSectionType, frozenset[str]] = {
        ResumeSectionType.SUMMARY: frozenset(
            {
                "summary",
                "professional summary",
                "profile",
                "professional profile",
                "career summary",
                "career profile",
                "objective",
                "career objective",
            }
        ),
        ResumeSectionType.EXPERIENCE: frozenset(
            {
                "experience",
                "work experience",
                "professional experience",
                "employment",
                "employment history",
                "work history",
                "professional history",
            }
        ),
        ResumeSectionType.EDUCATION: frozenset(
            {
                "education",
                "educational background",
                "academic background",
                "academic qualifications",
                "qualifications",
            }
        ),
        ResumeSectionType.PROJECTS: frozenset(
            {
                "projects",
                "personal projects",
                "academic projects",
                "professional projects",
                "project experience",
            }
        ),
        ResumeSectionType.CERTIFICATIONS: frozenset(
            {
                "certifications",
                "certificates",
                "professional certifications",
                "licenses and certifications",
                "licenses & certifications",
            }
        ),
        ResumeSectionType.SKILLS: frozenset(
            {
                "skills",
                "technical skills",
                "technical competencies",
                "core competencies",
                "key skills",
                "professional skills",
                "technologies",
                "technical expertise",
                "skills and technologies",
            }
        ),
    }

    def interpret(self, document: ParsedDocument) -> StructuredResume:
        """Interpret a parsed resume without reparsing the source document."""
        sections: list[ResumeSection] = []

        current_type = ResumeSectionType.HEADER
        current_heading: str | None = None
        current_blocks: list[DocumentBlock] = []

        for block in document.blocks:
            heading_type = self._classify_heading(block)

            if heading_type is not None:
                if current_blocks or current_heading is not None:
                    sections.append(
                        ResumeSection(
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
                ResumeSection(
                    section_type=current_type,
                    heading=current_heading,
                    blocks=tuple(current_blocks),
                )
            )

        return StructuredResume(
            document_id=document.document_id,
            sections=tuple(sections),
        )

    def _classify_heading(
        self,
        block: DocumentBlock,
    ) -> ResumeSectionType | None:
        """
        Return a semantic section type when a block is a resume heading.

        Some PDF parsers preserve text but do not reliably mark visual
        headings as DocumentBlockType.HEADING. Known section-title text is
        therefore accepted as a heading regardless of the parser block type.
        Unknown paragraph text is still treated as normal content.
        """
        normalized = self._normalize_heading(block.text)

        for section_type, aliases in self._SECTION_ALIASES.items():
            if normalized in aliases:
                return section_type

        if block.block_type == DocumentBlockType.HEADING:
            return ResumeSectionType.UNKNOWN

        return None

    @staticmethod
    def _normalize_heading(text: str) -> str:
        """Normalize heading text for alias matching."""
        normalized = " ".join(text.strip().lower().split())
        normalized = normalized.rstrip(":")
        return normalized