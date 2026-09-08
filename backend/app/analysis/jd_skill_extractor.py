from __future__ import annotations

from dataclasses import dataclass, field
import re

from backend.app.analysis.jd_structure import (
    JDSectionType,
    StructuredJobDescription,
)
from backend.app.infrastructure.parsers.models import DocumentBlock


class JDSkillEvidenceType:
    """Evidence classifications for job-description skill mentions."""

    EXPLICIT = "explicit"
    CONTEXTUAL = "contextual"


@dataclass(frozen=True)
class JDSkillMention:
    """A candidate skill mention extracted from job-description evidence."""

    raw_text: str
    section_type: JDSectionType
    evidence_type: str
    block: DocumentBlock
    start_offset: int
    end_offset: int
    extractor: str
    confidence: float
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class JDSkillExtractionResult:
    """All candidate skill mentions extracted from a structured JD."""

    document_id: str
    mentions: tuple[JDSkillMention, ...] = field(default_factory=tuple)


class SkillVocabularySource:
    """
    Read the canonical Phase 3 skill vocabulary without duplicating it.

    The source remains SkillNormalizer. This adapter exists only so the JD
    extractor can use the same detection vocabulary without coupling its
    mention model to the resume-specific SkillMention type.
    """

    @staticmethod
    def canonical_skills() -> tuple[str, ...]:
        from backend.app.analysis.skill_normalizer import SkillNormalizer

        return tuple(SkillNormalizer._CANONICAL_SKILLS.keys())

    @staticmethod
    def aliases() -> tuple[str, ...]:
        from backend.app.analysis.skill_normalizer import SkillNormalizer

        return tuple(SkillNormalizer._ALIASES.keys())


class JDSkillExtractor:
    """
    Extract candidate skills from a structured job description.

    This component performs candidate detection only. It does not perform
    normalization, ESCO mapping, matching, scoring, or XAI.
    """

    _EXPLICIT_SECTIONS = frozenset(
        {
            JDSectionType.SKILLS,
            JDSectionType.REQUIRED_QUALIFICATIONS,
            JDSectionType.PREFERRED_QUALIFICATIONS,
        }
    )

    _CONTEXTUAL_SECTIONS = frozenset(
        {
            JDSectionType.SUMMARY,
            JDSectionType.RESPONSIBILITIES,
            JDSectionType.EXPERIENCE,
        }
    )

    # Reuse the existing Phase 3 vocabulary as the single source of truth.
    _KNOWN_SKILLS: tuple[str, ...] = tuple(
        dict.fromkeys(
            (
                *SkillVocabularySource.canonical_skills(),
                *SkillVocabularySource.aliases(),
            )
        )
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

    def extract(
        self,
        document: StructuredJobDescription,
    ) -> JDSkillExtractionResult:
        """Extract candidate skills while preserving source order and evidence."""
        mentions: list[JDSkillMention] = []

        for section in document.sections:
            evidence_type = self._evidence_type(section.section_type)
            if evidence_type is None:
                continue

            for block in section.blocks:
                mentions.extend(
                    self._extract_from_block(
                        block=block,
                        section_type=section.section_type,
                        evidence_type=evidence_type,
                    )
                )

        return JDSkillExtractionResult(
            document_id=document.document_id,
            mentions=tuple(mentions),
        )

    def _extract_from_block(
        self,
        *,
        block: DocumentBlock,
        section_type: JDSectionType,
        evidence_type: str,
    ) -> list[JDSkillMention]:
        """Extract known candidate skills from one JD document block."""
        mentions: list[JDSkillMention] = []

        for match in self._SKILL_PATTERN.finditer(block.text):
            raw_text = match.group(1)
            confidence = (
                0.95
                if evidence_type == JDSkillEvidenceType.EXPLICIT
                else 0.80
            )

            mentions.append(
                JDSkillMention(
                    raw_text=raw_text,
                    section_type=section_type,
                    evidence_type=evidence_type,
                    block=block,
                    start_offset=match.start(1),
                    end_offset=match.end(1),
                    extractor="deterministic_jd_skill_lexicon",
                    confidence=confidence,
                )
            )

        return mentions

    @staticmethod
    def _evidence_type(section_type: JDSectionType) -> str | None:
        if section_type in JDSkillExtractor._EXPLICIT_SECTIONS:
            return JDSkillEvidenceType.EXPLICIT
        if section_type in JDSkillExtractor._CONTEXTUAL_SECTIONS:
            return JDSkillEvidenceType.CONTEXTUAL
        return None
