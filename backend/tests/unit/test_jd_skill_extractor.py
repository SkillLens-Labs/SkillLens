from __future__ import annotations

from backend.app.analysis.jd_skill_extractor import (
    JDSkillEvidenceType,
    JDSkillExtractor,
)
from backend.app.analysis.jd_structure import (
    JDSection,
    JDSectionType,
    StructuredJobDescription,
)
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    SourceLocation,
)


def make_block(
    text: str,
    block_type: DocumentBlockType = DocumentBlockType.BULLET,
    index: int = 0,
) -> DocumentBlock:
    return DocumentBlock(
        text=text,
        block_type=block_type,
        source=SourceLocation(block_index=index),
    )


def make_jd(*sections: JDSection) -> StructuredJobDescription:
    return StructuredJobDescription(
        document_id="jd-001",
        sections=sections,
    )


def test_extracts_skills_from_explicit_skills_section() -> None:
    jd = make_jd(
        JDSection(
            section_type=JDSectionType.SKILLS,
            heading="Technical Skills",
            blocks=(
                make_block("Python, FastAPI, SQL and Docker", index=1),
            ),
        )
    )

    result = JDSkillExtractor().extract(jd)

    assert [mention.raw_text for mention in result.mentions] == [
        "Python",
        "FastAPI",
        "SQL",
        "Docker",
    ]
    assert all(
        mention.evidence_type == JDSkillEvidenceType.EXPLICIT
        for mention in result.mentions
    )


def test_extracts_contextual_skills_from_responsibilities() -> None:
    jd = make_jd(
        JDSection(
            section_type=JDSectionType.RESPONSIBILITIES,
            heading="Responsibilities",
            blocks=(
                make_block(
                    "Build backend services using Python and FastAPI.",
                    index=1,
                ),
            ),
        )
    )

    result = JDSkillExtractor().extract(jd)

    assert [mention.raw_text for mention in result.mentions] == [
        "Python",
        "FastAPI",
    ]
    assert all(
        mention.evidence_type == JDSkillEvidenceType.CONTEXTUAL
        for mention in result.mentions
    )


def test_extracts_skills_from_required_and_preferred_sections() -> None:
    jd = make_jd(
        JDSection(
            section_type=JDSectionType.REQUIRED_QUALIFICATIONS,
            heading="Required Qualifications",
            blocks=(make_block("Python and SQL"),),
        ),
        JDSection(
            section_type=JDSectionType.PREFERRED_QUALIFICATIONS,
            heading="Preferred Qualifications",
            blocks=(make_block("Docker and Kubernetes"),),
        ),
    )

    result = JDSkillExtractor().extract(jd)

    assert [mention.raw_text for mention in result.mentions] == [
        "Python",
        "SQL",
        "Docker",
        "Kubernetes",
    ]
    assert [
        mention.evidence_type for mention in result.mentions
    ] == [
        JDSkillEvidenceType.EXPLICIT,
        JDSkillEvidenceType.EXPLICIT,
        JDSkillEvidenceType.EXPLICIT,
        JDSkillEvidenceType.EXPLICIT,
    ]


def test_preserves_original_skill_text_and_offsets() -> None:
    text = "Experienced with Python and PostgreSQL."

    jd = make_jd(
        JDSection(
            section_type=JDSectionType.SKILLS,
            heading="Skills",
            blocks=(make_block(text),),
        )
    )

    result = JDSkillExtractor().extract(jd)

    python_mention = result.mentions[0]

    assert python_mention.raw_text == "Python"
    assert (
        text[python_mention.start_offset : python_mention.end_offset]
        == "Python"
    )


def test_matching_is_case_insensitive_but_preserves_source_text() -> None:
    jd = make_jd(
        JDSection(
            section_type=JDSectionType.SKILLS,
            heading="Skills",
            blocks=(make_block("python, FASTAPI, sql"),),
        )
    )

    result = JDSkillExtractor().extract(jd)

    assert [mention.raw_text for mention in result.mentions] == [
        "python",
        "FASTAPI",
        "sql",
    ]


def test_supports_existing_skill_aliases() -> None:
    jd = make_jd(
        JDSection(
            section_type=JDSectionType.SKILLS,
            heading="Skills",
            blocks=(make_block("Py, ReactJS, Postgres and ML"),),
        )
    )

    result = JDSkillExtractor().extract(jd)

    assert [mention.raw_text for mention in result.mentions] == [
        "Py",
        "ReactJS",
        "Postgres",
        "ML",
    ]


def test_contextual_extraction_has_lower_confidence_than_explicit() -> None:
    jd = make_jd(
        JDSection(
            section_type=JDSectionType.SKILLS,
            heading="Skills",
            blocks=(make_block("Python"),),
        ),
        JDSection(
            section_type=JDSectionType.RESPONSIBILITIES,
            heading="Responsibilities",
            blocks=(make_block("Build Python services"),),
        ),
    )

    result = JDSkillExtractor().extract(jd)

    explicit = result.mentions[0]
    contextual = result.mentions[1]

    assert explicit.confidence > contextual.confidence
    assert explicit.confidence == 0.95
    assert contextual.confidence == 0.80


def test_preserves_document_provenance() -> None:
    block = make_block(
        "Python and Docker",
        DocumentBlockType.BULLET,
        42,
    )

    jd = make_jd(
        JDSection(
            section_type=JDSectionType.SKILLS,
            heading="Skills",
            blocks=(block,),
        )
    )

    result = JDSkillExtractor().extract(jd)

    assert all(mention.block is block for mention in result.mentions)
    assert all(
        mention.block.source.block_index == 42
        for mention in result.mentions
    )


def test_preserves_document_id() -> None:
    jd = make_jd(
        JDSection(
            section_type=JDSectionType.SKILLS,
            heading="Skills",
            blocks=(make_block("Python"),),
        )
    )

    result = JDSkillExtractor().extract(jd)

    assert result.document_id == "jd-001"


def test_ignores_unrelated_sections() -> None:
    jd = make_jd(
        JDSection(
            section_type=JDSectionType.HEADER,
            heading="Python Developer",
            blocks=(make_block("Python"),),
        ),
        JDSection(
            section_type=JDSectionType.UNKNOWN,
            heading="Company Awards",
            blocks=(make_block("Python programming competition"),),
        ),
    )

    result = JDSkillExtractor().extract(jd)

    assert result.mentions == ()


def test_preserves_source_order_across_sections_and_blocks() -> None:
    jd = make_jd(
        JDSection(
            section_type=JDSectionType.SKILLS,
            heading="Skills",
            blocks=(
                make_block("Python", index=1),
                make_block("React", index=2),
            ),
        ),
        JDSection(
            section_type=JDSectionType.RESPONSIBILITIES,
            heading="Responsibilities",
            blocks=(
                make_block("Use Docker", index=3),
            ),
        ),
    )

    result = JDSkillExtractor().extract(jd)

    assert [mention.raw_text for mention in result.mentions] == [
        "Python",
        "React",
        "Docker",
    ]
