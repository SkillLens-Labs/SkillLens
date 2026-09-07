from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from backend.app.analysis.skill_normalizer import NormalizedSkill


class ESCOMapStatus(StrEnum):
    MAPPED = "mapped"
    AMBIGUOUS = "ambiguous"
    UNMAPPED = "unmapped"


@dataclass(frozen=True)
class ESCOCandidate:
    """A candidate ESCO skill concept."""

    uri: str
    preferred_label: str
    confidence: float


@dataclass(frozen=True)
class ESCOMapResult:
    """Result of mapping one normalized skill to ESCO."""

    raw_text: str
    canonical_name: str
    status: ESCOMapStatus
    candidates: tuple[ESCOCandidate, ...] = field(default_factory=tuple)
    esco_version: str = "1.2.1"
    mapping_method: str = "deterministic_lookup"


class ESCOMapper:
    """Map normalized skills to a versioned ESCO skill vocabulary.

    The mapper intentionally owns the ESCO boundary. It does not perform
    extraction, normalization, matching, scoring, or recommendations.
    """

    ESCO_VERSION = "1.2.1"

    # This is a small deterministic adapter vocabulary for the initial
    # Phase 3 implementation. The complete ESCO dataset should remain an
    # external/versioned data artifact rather than being hardcoded here.
    _MAPPINGS: dict[str, tuple[ESCOCandidate, ...]] = {
        "python": (
            ESCOCandidate(
                uri="",
                preferred_label="Python",
                confidence=0.99,
            ),
        ),
        "java": (
            ESCOCandidate(
                uri="",
                preferred_label="Java",
                confidence=0.99,
            ),
        ),
        "javascript": (
            ESCOCandidate(
                uri="",
                preferred_label="JavaScript",
                confidence=0.99,
            ),
        ),
        "sql": (
            ESCOCandidate(
                uri="",
                preferred_label="SQL",
                confidence=0.99,
            ),
        ),
        "react": (
            ESCOCandidate(
                uri="",
                preferred_label="React",
                confidence=0.98,
            ),
        ),
        "docker": (
            ESCOCandidate(
                uri="",
                preferred_label="Docker",
                confidence=0.98,
            ),
        ),
        "kubernetes": (
            ESCOCandidate(
                uri="",
                preferred_label="Kubernetes",
                confidence=0.98,
            ),
        ),
        "machine learning": (
            ESCOCandidate(
                uri="",
                preferred_label="Machine learning",
                confidence=0.97,
            ),
        ),
        "data analysis": (
            ESCOCandidate(
                uri="",
                preferred_label="Data analysis",
                confidence=0.97,
            ),
        ),
    }

    def map(self, skill: NormalizedSkill) -> ESCOMapResult:
        """Map one normalized skill to ESCO."""
        candidates = self._MAPPINGS.get(skill.canonical_name)

        if candidates is None:
            return ESCOMapResult(
                raw_text=skill.raw_text,
                canonical_name=skill.canonical_name,
                status=ESCOMapStatus.UNMAPPED,
                candidates=(),
                esco_version=self.ESCO_VERSION,
            )

        if len(candidates) > 1:
            return ESCOMapResult(
                raw_text=skill.raw_text,
                canonical_name=skill.canonical_name,
                status=ESCOMapStatus.AMBIGUOUS,
                candidates=candidates,
                esco_version=self.ESCO_VERSION,
                mapping_method="deterministic_lookup_ambiguous",
            )

        return ESCOMapResult(
            raw_text=skill.raw_text,
            canonical_name=skill.canonical_name,
            status=ESCOMapStatus.MAPPED,
            candidates=candidates,
            esco_version=self.ESCO_VERSION,
        )

    def map_many(
        self,
        skills: tuple[NormalizedSkill, ...] | list[NormalizedSkill],
    ) -> tuple[ESCOMapResult, ...]:
        """Map normalized skills while preserving source order."""
        return tuple(self.map(skill) for skill in skills)