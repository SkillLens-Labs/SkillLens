"""SkillLens V2 skill normalization (resume side).

Canonical-resolve extracted skill mentions using the shared taxonomy
(skill_taxonomy.py). The legacy ``_CANONICAL_SKILLS`` and ``_ALIASES``
class attributes are kept as derived views so existing callers (notably
the JD-side extractor) continue to work unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
import unicodedata

from backend.app.analysis.skill_extractor import SkillMention
from backend.app.analysis.skill_taxonomy import Taxonomy


@dataclass(frozen=True)
class NormalizedSkill:
    """A skill mention resolved to a deterministic canonical name."""

    raw_text: str
    canonical_name: str
    mention: SkillMention
    matched_alias: str | None = None
    confidence: float = 1.0
    metadata: dict[str, object] = field(default_factory=dict)


class SkillNormalizer:
    """Normalize extracted skill mentions deterministically."""

    # Derived views of the shared taxonomy, kept for backwards
    # compatibility with existing callers.
    _CANONICAL_SKILLS: dict[str, str] = {
        name: name for name in Taxonomy.canonical_names
    }

    _ALIASES: dict[str, str] = Taxonomy.aliases

    def normalize(
        self,
        mention: SkillMention,
    ) -> NormalizedSkill:
        """Normalize one extracted skill mention."""
        raw_text = mention.raw_text
        normalized = self._normalize_text(raw_text)

        canonical_name = self._CANONICAL_SKILLS.get(normalized)

        if canonical_name is not None:
            return NormalizedSkill(
                raw_text=raw_text,
                canonical_name=canonical_name,
                mention=mention,
                confidence=mention.confidence,
                metadata={
                    "normalization_method": "canonical_lookup",
                    "category": Taxonomy.category_by_canonical.get(
                        canonical_name, "",
                    ),
                },
            )

        canonical_name = self._ALIASES.get(normalized)

        if canonical_name is not None:
            return NormalizedSkill(
                raw_text=raw_text,
                canonical_name=canonical_name,
                mention=mention,
                matched_alias=normalized,
                confidence=mention.confidence,
                metadata={
                    "normalization_method": "alias_lookup",
                    "category": Taxonomy.category_by_canonical.get(
                        canonical_name, "",
                    ),
                },
            )

        if canonical_name is None:
            # Case-sensitive aliases such as "Go", "AI", "R" arrive with
            # their original casing preserved by the extractor.
            case_canonical = Taxonomy.lookup_case_sensitive(raw_text)
            if case_canonical is not None:
                return NormalizedSkill(
                    raw_text=raw_text,
                    canonical_name=case_canonical,
                    mention=mention,
                    matched_alias=raw_text,
                    confidence=mention.confidence,
                    metadata={
                        "normalization_method": "case_sensitive_alias",
                        "category": Taxonomy.category_by_canonical.get(
                            case_canonical, "",
                        ),
                    },
                )

        stripped_name = self._strip_generic_suffix(normalized)
        if stripped_name != normalized:
            stripped_canonical = self._CANONICAL_SKILLS.get(stripped_name)
            if stripped_canonical is None:
                stripped_canonical = self._ALIASES.get(stripped_name)
            if stripped_canonical is not None:
                return NormalizedSkill(
                    raw_text=raw_text,
                    canonical_name=stripped_canonical,
                    mention=mention,
                    matched_alias=stripped_name,
                    confidence=mention.confidence,
                    metadata={
                        "normalization_method": "alias_lookup",
                        "category": Taxonomy.category_by_canonical.get(
                            stripped_canonical, "",
                        ),
                    },
                )

        # The extractor should normally prevent this path. Keeping it
        # deterministic makes the normalizer safe when used independently.
        return NormalizedSkill(
            raw_text=raw_text,
            canonical_name=normalized,
            mention=mention,
            confidence=mention.confidence,
            metadata={
                "normalization_method": "normalized_fallback",
            },
        )

    def normalize_many(
        self,
        mentions: tuple[SkillMention, ...] | list[SkillMention],
    ) -> tuple[NormalizedSkill, ...]:
        """Normalize multiple extracted skill mentions in source order."""
        return tuple(self.normalize(mention) for mention in mentions)

    @staticmethod
    def _strip_generic_suffix(normalized: str) -> str:
        """Strip generic qualifier suffixes such as 'python programming'."""
        return re.sub(
            r"\s+(programming|development|skills)$",
            "",
            normalized,
        )

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Apply deterministic text normalization."""
        normalized = unicodedata.normalize("NFKC", text)
        normalized = normalized.strip().lower()
        normalized = re.sub(r"\s+", " ", normalized)

        # Normalize common typographic separators without changing
        # meaningful skill punctuation such as C++, C#, or Node.js.
        normalized = normalized.replace("–", "-")
        normalized = normalized.replace("—", "-")

        return normalized
