from __future__ import annotations

from backend.app.analysis.resume_structure import (
    ResumeSection,
    ResumeSectionType,
    StructuredResume,
)
from backend.app.analysis.skill_extractor import (
    SkillEvidenceType,
    SkillExtractor,
)
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    SourceLocation,
)


def make_block(
    text: str,
    block_type: DocumentBlockType = DocumentBlockType.PARAGRAPH,
    index: int = 0,
) -> DocumentBlock:
    return DocumentBlock(
        text=text,
        block_type=block_type,
        source=SourceLocation(block_index=index),
    )


def make_resume(
    *sections: ResumeSection,
) -> StructuredResume:
    return StructuredResume(
        document_id="resume-001",
        sections=sections,
    )


def test_extracts_skills_from_explicit_skills_section() -> None:
    resume = make_resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Technical Skills",
            blocks=(
                make_block(
                    "Python, FastAPI, SQL and Docker",
                    DocumentBlockType.BULLET,
                    1,
                ),
            ),
        )
    )

    result = SkillExtractor().extract(resume)

    assert [mention.raw_text for mention in result.mentions] == [
        "Python",
        "FastAPI",
        "SQL",
        "Docker",
    ]

    assert all(
        mention.evidence_type == SkillEvidenceType.EXPLICIT
        for mention in result.mentions
    )


def test_extracts_contextual_skills_from_experience() -> None:
    resume = make_resume(
        ResumeSection(
            section_type=ResumeSectionType.EXPERIENCE,
            heading="Experience",
            blocks=(
                make_block(
                    "Built backend services using Python and FastAPI.",
                    DocumentBlockType.BULLET,
                    1,
                ),
            ),
        )
    )

    result = SkillExtractor().extract(resume)

    assert [mention.raw_text for mention in result.mentions] == [
        "Python",
        "FastAPI",
    ]

    assert all(
        mention.evidence_type == SkillEvidenceType.CONTEXTUAL
        for mention in result.mentions
    )


def test_preserves_original_skill_text_and_offsets() -> None:
    text = "Experienced with Python and PostgreSQL."
    resume = make_resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(make_block(text),),
        )
    )

    result = SkillExtractor().extract(resume)

    python_mention = result.mentions[0]

    assert python_mention.raw_text == "Python"
    assert text[python_mention.start_offset : python_mention.end_offset] == "Python"


def test_matching_is_case_insensitive_but_preserves_source_text() -> None:
    resume = make_resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(
                make_block("python, FASTAPI, sql"),
            ),
        )
    )

    result = SkillExtractor().extract(resume)

    assert [mention.raw_text for mention in result.mentions] == [
        "python",
        "FASTAPI",
        "sql",
    ]


def test_does_not_extract_skills_from_unrelated_sections() -> None:
    resume = make_resume(
        ResumeSection(
            section_type=ResumeSectionType.HEADER,
            heading=None,
            blocks=(
                make_block(
                    "Candidate Name - Python Developer",
                ),
            ),
        ),
        ResumeSection(
            section_type=ResumeSectionType.UNKNOWN,
            heading="Awards",
            blocks=(
                make_block(
                    "Winner of Python programming competition",
                ),
            ),
        ),
    )

    result = SkillExtractor().extract(resume)

    assert result.mentions == ()


def test_contextual_extraction_has_lower_confidence_than_explicit() -> None:
    resume = make_resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(make_block("Python"),),
        ),
        ResumeSection(
            section_type=ResumeSectionType.PROJECTS,
            heading="Projects",
            blocks=(
                make_block("Built a Python application"),
            ),
        ),
    )

    result = SkillExtractor().extract(resume)

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

    resume = make_resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(block,),
        )
    )

    result = SkillExtractor().extract(resume)

    assert all(mention.block is block for mention in result.mentions)
    assert all(
        mention.block.source.block_index == 42
        for mention in result.mentions
    )


def test_preserves_document_id() -> None:
    resume = make_resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(make_block("Python"),),
        )
    )

    result = SkillExtractor().extract(resume)

    assert result.document_id == "resume-001"