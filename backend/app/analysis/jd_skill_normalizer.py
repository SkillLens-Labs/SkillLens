from __future__ import annotations

from backend.app.analysis.jd_skill_extractor import (
    JDSkillEvidenceType,
    JDSkillMention,
)
from backend.app.analysis.resume_structure import ResumeSectionType
from backend.app.analysis.skill_extractor import (
    SkillEvidenceType,
    SkillMention,
)
from backend.app.analysis.skill_normalizer import (
    NormalizedSkill,
    SkillNormalizer,
)


class JDSkillNormalizer:
    """
    Adapt JD skill mentions to the existing Phase 3 skill normalizer.

    The existing SkillNormalizer remains unchanged. This adapter creates the
    minimal temporary SkillMention required by that contract and returns the
    existing NormalizedSkill model used by ESCOMapper.
    """

    def __init__(
        self,
        *,
        normalizer: SkillNormalizer | None = None,
    ) -> None:
        self._normalizer = normalizer or SkillNormalizer()

    def normalize(self, mention: JDSkillMention) -> NormalizedSkill:
        """
        Normalize one JD skill mention using the existing canonical vocabulary.
        """
        resume_compatible_mention = SkillMention(
            raw_text=mention.raw_text,
            section_type=ResumeSectionType.UNKNOWN,
            evidence_type=self._map_evidence_type(mention),
            block=mention.block,
            start_offset=mention.start_offset,
            end_offset=mention.end_offset,
            extractor=mention.extractor,
            confidence=mention.confidence,
            metadata={
                **mention.metadata,
                "source": "job_description",
                "jd_section_type": mention.section_type.value,
            },
        )

        normalized = self._normalizer.normalize(resume_compatible_mention)

        return NormalizedSkill(
            raw_text=normalized.raw_text,
            canonical_name=normalized.canonical_name,
            mention=normalized.mention,
            matched_alias=normalized.matched_alias,
            confidence=normalized.confidence,
            metadata={
                **normalized.metadata,
                "source": "job_description",
                "jd_section_type": mention.section_type.value,
            },
        )

    def normalize_many(
        self,
        mentions: tuple[JDSkillMention, ...] | list[JDSkillMention],
    ) -> tuple[NormalizedSkill, ...]:
        """Normalize JD skill mentions while preserving source order."""
        return tuple(self.normalize(mention) for mention in mentions)

    @staticmethod
    def _map_evidence_type(mention: JDSkillMention) -> SkillEvidenceType:
        if mention.evidence_type == JDSkillEvidenceType.EXPLICIT:
            return SkillEvidenceType.EXPLICIT
        return SkillEvidenceType.CONTEXTUAL
