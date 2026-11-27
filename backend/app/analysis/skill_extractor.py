"""SkillLens V2 skill extraction (resume side).

Candidate detection now runs on the shared skill taxonomy
(skill_taxonomy.py) instead of a local hardcoded list, so every skill the
normalizer, matcher or JD side can understand is also detectable here.
Matching is regex-based and deterministic, with a case-sensitive rule for
ambiguous short aliases such as "Go", "R" and "C".

Backwards compatible: SkillMention, SkillExtractionResult, the extraction
section sets, the extractor label and the confidence values are unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re

from backend.app.analysis.resume_structure import (
    ResumeSectionType,
    StructuredResume,
)
from backend.app.analysis.skill_taxonomy import Taxonomy
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

    # Candidate-detection vocabulary, shared with the normalizer and the
    # JD-side extractor. Canonical names and multi-word aliases are matched
    # case-insensitively; ambiguous short aliases (see case_sensitive_aliases
    # in the taxonomy) are matched case-sensitively with strict boundaries
    # instead, so "Go", "R", "C" and "AI" never fire inside ordinary words.
    _KNOWN_SKILLS: tuple[str, ...] = Taxonomy.canonical_names

    _CASE_SENSITIVE_KEYS = frozenset(
        key.lower() for key in Taxonomy.case_sensitive_alias_to_canonical
    )

    _SKILL_PATTERN = re.compile(
        r"(?<!\w)"
        + "("
        + "|".join(
            re.escape(term)
            for term in sorted(
                (*Taxonomy.canonical_names, *Taxonomy.aliases),
                key=lambda term: (-len(term), term),
            )
            if term.lower() not in _CASE_SENSITIVE_KEYS
        )
        + r")(?![\w&])",
        re.IGNORECASE,
    )

    _STRICT_PATTERN = re.compile(
        r"(?<!\w)"
        + "("
        + "|".join(
            re.escape(term)
            for term in sorted(
                Taxonomy.case_sensitive_alias_to_canonical,
                key=lambda term: (-len(term), term),
            )
        )
        + r")(?![\w&])",
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
        matched_spans: list[tuple[int, int]] = []

        confidence = (
            0.95
            if evidence_type == SkillEvidenceType.EXPLICIT
            else 0.80
        )

        def add_match(start: int, end: int, raw_text: str) -> None:
            for matched_start, matched_end in matched_spans:
                if start < matched_end and matched_start < end:
                    return  # already covered by an earlier, longer match
            matched_spans.append((start, end))
            mentions.append(
                SkillMention(
                    raw_text=raw_text,
                    section_type=section_type,
                    evidence_type=evidence_type,
                    block=block,
                    start_offset=start,
                    end_offset=end,
                    extractor="deterministic_skill_lexicon",
                    confidence=confidence,
                    metadata={"category": Taxonomy.category_by_canonical.get(
                        Taxonomy.resolve(raw_text) or "", ""
                    )},
                )
            )

        for match in self._SKILL_PATTERN.finditer(block.text):
            add_match(match.start(1), match.end(1), match.group(1))

        for match in self._STRICT_PATTERN.finditer(block.text):
            add_match(match.start(1), match.end(1), match.group(1))

        mentions.sort(key=lambda mention: (mention.start_offset, mention.end_offset))
        return mentions
