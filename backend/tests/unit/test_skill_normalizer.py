from __future__ import annotations

from backend.app.analysis.resume_structure import (
    ResumeSectionType,
)
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


def make_mention(
    text: str,
    index: int = 0,
) -> SkillMention:
    block = DocumentBlock(
        text=text,
        block_type=DocumentBlockType.BULLET,
        source=SourceLocation(block_index=index),
    )

    return SkillMention(
        raw_text=text,
        section_type=ResumeSectionType.SKILLS,
        evidence_type=SkillEvidenceType.EXPLICIT,
        block=block,
        start_offset=0,
        end_offset=len(text),
        extractor="test",
        confidence=0.95,
    )


def test_normalizes_canonical_skill() -> None:
    mention = make_mention("Python")

    result = SkillNormalizer().normalize(mention)

    assert result.raw_text == "Python"
    assert result.canonical_name == "python"
    assert result.matched_alias is None


def test_normalizes_skill_case_insensitively() -> None:
    mention = make_mention("FASTAPI")

    result = SkillNormalizer().normalize(mention)

    assert result.canonical_name == "fastapi"


def test_resolves_python_aliases() -> None:
    normalizer = SkillNormalizer()

    assert normalizer.normalize(make_mention("Py")).canonical_name == "python"
    assert (
        normalizer.normalize(make_mention("Python Programming")).canonical_name
        == "python"
    )
    assert normalizer.normalize(make_mention("Python3")).canonical_name == "python"


def test_resolves_javascript_aliases() -> None:
    normalizer = SkillNormalizer()

    assert normalizer.normalize(make_mention("JS")).canonical_name == "javascript"
    assert (
        normalizer.normalize(make_mention("javascript programming")).canonical_name
        == "javascript"
    )


def test_resolves_react_aliases() -> None:
    normalizer = SkillNormalizer()

    assert normalizer.normalize(make_mention("ReactJS")).canonical_name == "react"
    assert normalizer.normalize(make_mention("React.js")).canonical_name == "react"
    assert normalizer.normalize(make_mention("React JS")).canonical_name == "react"


def test_resolves_database_aliases() -> None:
    normalizer = SkillNormalizer()

    assert normalizer.normalize(make_mention("Postgres")).canonical_name == "postgresql"
    assert normalizer.normalize(make_mention("Mongo")).canonical_name == "mongodb"


def test_resolves_ml_alias() -> None:
    result = SkillNormalizer().normalize(make_mention("ML"))

    assert result.canonical_name == "machine learning"


def test_resolves_scikit_learn_aliases() -> None:
    normalizer = SkillNormalizer()

    assert (
        normalizer.normalize(make_mention("sklearn")).canonical_name
        == "scikit-learn"
    )
    assert (
        normalizer.normalize(make_mention("scikit learn")).canonical_name
        == "scikit-learn"
    )


def test_preserves_original_text() -> None:
    mention = make_mention("  Python  ")

    result = SkillNormalizer().normalize(mention)

    assert result.raw_text == "  Python  "
    assert result.canonical_name == "python"


def test_preserves_extraction_confidence() -> None:
    mention = make_mention("Python")
    result = SkillNormalizer().normalize(mention)

    assert result.confidence == mention.confidence


def test_records_alias_normalization_method() -> None:
    result = SkillNormalizer().normalize(make_mention("Py"))

    assert result.matched_alias == "py"
    assert result.metadata["normalization_method"] == "alias_lookup"


def test_records_canonical_normalization_method() -> None:
    result = SkillNormalizer().normalize(make_mention("Python"))

    assert result.metadata["normalization_method"] == "canonical_lookup"


def test_normalize_many_preserves_source_order() -> None:
    mentions = [
        make_mention("Python", 1),
        make_mention("ReactJS", 2),
        make_mention("Postgres", 3),
    ]

    result = SkillNormalizer().normalize_many(mentions)

    assert [skill.raw_text for skill in result] == [
        "Python",
        "ReactJS",
        "Postgres",
    ]

    assert [skill.canonical_name for skill in result] == [
        "python",
        "react",
        "postgresql",
    ]