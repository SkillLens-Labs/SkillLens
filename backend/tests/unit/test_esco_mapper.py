from __future__ import annotations

from backend.app.analysis.esco_mapper import (
    ESCOMapStatus,
    ESCOMapper,
)
from backend.app.analysis.resume_structure import ResumeSectionType
from backend.app.analysis.skill_extractor import (
    SkillEvidenceType,
    SkillMention,
)
from backend.app.analysis.skill_normalizer import (
    SkillNormalizer,
)
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    SourceLocation,
)


def make_normalized_skill(text: str):
    block = DocumentBlock(
        text=text,
        block_type=DocumentBlockType.BULLET,
        source=SourceLocation(block_index=0),
    )

    mention = SkillMention(
        raw_text=text,
        section_type=ResumeSectionType.SKILLS,
        evidence_type=SkillEvidenceType.EXPLICIT,
        block=block,
        start_offset=0,
        end_offset=len(text),
        extractor="test",
        confidence=0.95,
    )

    return SkillNormalizer().normalize(mention)


def test_maps_known_skill() -> None:
    skill = make_normalized_skill("Python")

    result = ESCOMapper().map(skill)

    assert result.status == ESCOMapStatus.MAPPED
    assert result.canonical_name == "python"
    assert len(result.candidates) == 1
    assert result.candidates[0].preferred_label == "Python"


def test_mapping_is_case_insensitive_through_normalized_input() -> None:
    skill = make_normalized_skill("PYTHON")

    result = ESCOMapper().map(skill)

    assert result.status == ESCOMapStatus.MAPPED
    assert result.canonical_name == "python"


def test_unmapped_skill_is_explicitly_reported() -> None:
    skill = make_normalized_skill("FastAPI")

    result = ESCOMapper().map(skill)

    assert result.status == ESCOMapStatus.UNMAPPED
    assert result.candidates == ()


def test_mapping_preserves_raw_text() -> None:
    skill = make_normalized_skill("ReactJS")

    result = ESCOMapper().map(skill)

    assert result.raw_text == "ReactJS"
    assert result.canonical_name == "react"


def test_mapping_contains_version_metadata() -> None:
    skill = make_normalized_skill("Python")

    result = ESCOMapper().map(skill)

    assert result.esco_version == "1.2.1"


def test_mapping_preserves_source_order() -> None:
    normalizer = SkillNormalizer()
    mapper = ESCOMapper()

    skills = [
        make_normalized_skill("Python"),
        make_normalized_skill("ReactJS"),
        make_normalized_skill("FastAPI"),
    ]

    results = mapper.map_many(skills)

    assert [result.raw_text for result in results] == [
        "Python",
        "ReactJS",
        "FastAPI",
    ]

    assert [result.status for result in results] == [
        ESCOMapStatus.MAPPED,
        ESCOMapStatus.MAPPED,
        ESCOMapStatus.UNMAPPED,
    ]


def test_mapped_candidate_contains_confidence() -> None:
    skill = make_normalized_skill("Machine Learning")

    result = ESCOMapper().map(skill)

    assert result.status == ESCOMapStatus.MAPPED
    assert 0.0 <= result.candidates[0].confidence <= 1.0


def test_mapping_method_is_recorded() -> None:
    skill = make_normalized_skill("Python")

    result = ESCOMapper().map(skill)

    assert result.mapping_method == "deterministic_lookup"