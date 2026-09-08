from __future__ import annotations

from backend.app.analysis.jd_skill_extractor import (
    JDSkillEvidenceType,
    JDSkillExtractor,
)
from backend.app.analysis.jd_skill_normalizer import JDSkillNormalizer
from backend.app.analysis.jd_structure import (
    JDSection,
    JDSectionType,
    StructuredJobDescription,
)
from backend.app.analysis.skill_normalizer import NormalizedSkill
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    SourceLocation,
)


def make_block(
    text: str,
    index: int = 0,
) -> DocumentBlock:
    return DocumentBlock(
        text=text,
        block_type=DocumentBlockType.BULLET,
        source=SourceLocation(block_index=index),
    )


def make_mention(
    text: str,
    section_type: JDSectionType = JDSectionType.SKILLS,
    index: int = 0,
):
    jd = StructuredJobDescription(
        document_id="jd-001",
        sections=(
            JDSection(
                section_type=section_type,
                heading="Skills",
                blocks=(make_block(text, index),),
            ),
        ),
    )
    result = JDSkillExtractor().extract(jd)
    assert result.mentions
    return result.mentions[0]


def test_normalizes_canonical_skill() -> None:
    mention = make_mention("Python")

    result = JDSkillNormalizer().normalize(mention)

    assert isinstance(result, NormalizedSkill)
    assert result.raw_text == "Python"
    assert result.canonical_name == "python"
    assert result.matched_alias is None


def test_normalizes_existing_skill_alias() -> None:
    mention = make_mention("ReactJS")

    result = JDSkillNormalizer().normalize(mention)

    assert result.canonical_name == "react"
    assert result.matched_alias == "reactjs"
    assert result.metadata["normalization_method"] == "alias_lookup"


def test_preserves_jd_provenance() -> None:
    mention = make_mention(
        "Python",
        section_type=JDSectionType.REQUIRED_QUALIFICATIONS,
    )

    result = JDSkillNormalizer().normalize(mention)

    assert result.metadata["source"] == "job_description"
    assert (
        result.metadata["jd_section_type"]
        == JDSectionType.REQUIRED_QUALIFICATIONS.value
    )


def test_preserves_source_text_and_offsets() -> None:
    text = "Python"

    mention = make_mention(text)

    result = JDSkillNormalizer().normalize(mention)

    assert result.raw_text == mention.raw_text
    assert result.mention.start_offset == mention.start_offset
    assert result.mention.end_offset == mention.end_offset
    assert (
        result.mention.block.text[
            result.mention.start_offset : result.mention.end_offset
        ]
        == "Python"
    )


def test_preserves_extraction_confidence() -> None:
    mention = make_mention("Python")

    result = JDSkillNormalizer().normalize(mention)

    assert result.confidence == mention.confidence
    assert result.mention.confidence == mention.confidence


def test_preserves_explicit_evidence_type() -> None:
    mention = make_mention(
        "Python",
        section_type=JDSectionType.SKILLS,
    )

    assert mention.evidence_type == JDSkillEvidenceType.EXPLICIT

    result = JDSkillNormalizer().normalize(mention)

    assert result.mention.evidence_type == "explicit"


def test_preserves_contextual_evidence_type() -> None:
    mention = make_mention(
        "Python",
        section_type=JDSectionType.RESPONSIBILITIES,
    )

    assert mention.evidence_type == JDSkillEvidenceType.CONTEXTUAL

    result = JDSkillNormalizer().normalize(mention)

    assert result.mention.evidence_type == "contextual"


def test_normalize_many_preserves_source_order() -> None:
    jd = StructuredJobDescription(
        document_id="jd-001",
        sections=(
            JDSection(
                section_type=JDSectionType.SKILLS,
                heading="Skills",
                blocks=(
                    make_block("Python, ReactJS, Postgres", index=1),
                ),
            ),
        ),
    )

    mentions = JDSkillExtractor().extract(jd).mentions
    results = JDSkillNormalizer().normalize_many(mentions)

    assert [skill.raw_text for skill in results] == [
        "Python",
        "ReactJS",
        "Postgres",
    ]
    assert [skill.canonical_name for skill in results] == [
        "python",
        "react",
        "postgresql",
    ]


def test_jd_normalized_skill_can_be_consumed_by_esco_mapper() -> None:
    from backend.app.analysis.esco_mapper import ESCOMapStatus, ESCOMapper

    mention = make_mention("Python")
    normalized = JDSkillNormalizer().normalize(mention)

    result = ESCOMapper().map(normalized)

    assert result.status == ESCOMapStatus.MAPPED
    assert result.canonical_name == "python"
