from __future__ import annotations

from backend.app.analysis.resume_structure import (
    ResumeSectionType,
    ResumeStructureInterpreter,
)
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    DocumentType,
    ParsedDocument,
    SourceLocation,
)


def make_block(
    text: str,
    block_type: DocumentBlockType,
    index: int,
) -> DocumentBlock:
    return DocumentBlock(
        text=text,
        block_type=block_type,
        source=SourceLocation(block_index=index),
    )


def make_document(*blocks: DocumentBlock) -> ParsedDocument:
    return ParsedDocument(
        document_id="resume-001",
        document_type=DocumentType.DOCX,
        blocks=list(blocks),
    )


def test_interpreter_detects_common_resume_sections() -> None:
    document = make_document(
        make_block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
        make_block("Professional Summary", DocumentBlockType.HEADING, 1),
        make_block(
            "Software engineer with Python experience.",
            DocumentBlockType.PARAGRAPH,
            2,
        ),
        make_block("Work Experience", DocumentBlockType.HEADING, 3),
        make_block("Python Developer", DocumentBlockType.PARAGRAPH, 4),
        make_block("Education", DocumentBlockType.HEADING, 5),
        make_block("B.E. Computer Science", DocumentBlockType.PARAGRAPH, 6),
        make_block("Technical Skills", DocumentBlockType.HEADING, 7),
        make_block("Python, FastAPI, SQL", DocumentBlockType.BULLET, 8),
    )

    result = ResumeStructureInterpreter().interpret(document)

    assert [section.section_type for section in result.sections] == [
        ResumeSectionType.HEADER,
        ResumeSectionType.SUMMARY,
        ResumeSectionType.EXPERIENCE,
        ResumeSectionType.EDUCATION,
        ResumeSectionType.SKILLS,
    ]


def test_interpreter_supports_sections_in_unusual_order() -> None:
    document = make_document(
        make_block("Skills", DocumentBlockType.HEADING, 0),
        make_block("Python", DocumentBlockType.BULLET, 1),
        make_block("Projects", DocumentBlockType.HEADING, 2),
        make_block("SkillLens", DocumentBlockType.PARAGRAPH, 3),
        make_block("Education", DocumentBlockType.HEADING, 4),
        make_block("Computer Science", DocumentBlockType.PARAGRAPH, 5),
        make_block("Experience", DocumentBlockType.HEADING, 6),
        make_block("Software Engineer", DocumentBlockType.PARAGRAPH, 7),
    )

    result = ResumeStructureInterpreter().interpret(document)

    assert [
        section.section_type
        for section in result.sections
    ] == [
        ResumeSectionType.SKILLS,
        ResumeSectionType.PROJECTS,
        ResumeSectionType.EDUCATION,
        ResumeSectionType.EXPERIENCE,
    ]


def test_interpreter_handles_heading_aliases_and_colons() -> None:
    document = make_document(
        make_block("PROFILE:", DocumentBlockType.HEADING, 0),
        make_block("Summary text", DocumentBlockType.PARAGRAPH, 1),
        make_block("EMPLOYMENT HISTORY", DocumentBlockType.HEADING, 2),
        make_block("Developer", DocumentBlockType.PARAGRAPH, 3),
        make_block("CERTIFICATES:", DocumentBlockType.HEADING, 4),
        make_block("Certification", DocumentBlockType.PARAGRAPH, 5),
    )

    result = ResumeStructureInterpreter().interpret(document)

    assert [
        section.section_type
        for section in result.sections
    ] == [
        ResumeSectionType.SUMMARY,
        ResumeSectionType.EXPERIENCE,
        ResumeSectionType.CERTIFICATIONS,
    ]


def test_unknown_heading_does_not_get_forced_into_known_section() -> None:
    document = make_document(
        make_block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
        make_block("Awards & Honors", DocumentBlockType.HEADING, 1),
        make_block("Hackathon Winner", DocumentBlockType.PARAGRAPH, 2),
    )

    result = ResumeStructureInterpreter().interpret(document)

    assert result.sections[0].section_type == ResumeSectionType.HEADER
    assert result.sections[1].section_type == ResumeSectionType.UNKNOWN
    assert result.sections[1].heading == "Awards & Honors"


def test_non_heading_blocks_do_not_start_new_sections() -> None:
    document = make_document(
        make_block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
        make_block("Software Engineer", DocumentBlockType.PARAGRAPH, 1),
        make_block("Python", DocumentBlockType.BULLET, 2),
    )

    result = ResumeStructureInterpreter().interpret(document)

    assert len(result.sections) == 1
    assert result.sections[0].section_type == ResumeSectionType.HEADER
    assert [
        block.text
        for block in result.sections[0].blocks
    ] == [
        "Candidate Name",
        "Software Engineer",
        "Python",
    ]


def test_section_blocks_are_preserved_in_original_order() -> None:
    document = make_document(
        make_block("Experience", DocumentBlockType.HEADING, 0),
        make_block("Company A", DocumentBlockType.PARAGRAPH, 1),
        make_block("Developer", DocumentBlockType.PARAGRAPH, 2),
        make_block("Built APIs", DocumentBlockType.BULLET, 3),
    )

    result = ResumeStructureInterpreter().interpret(document)

    experience = result.sections_of(ResumeSectionType.EXPERIENCE)[0]

    assert [block.text for block in experience.blocks] == [
        "Company A",
        "Developer",
        "Built APIs",
    ]


def test_interpreter_preserves_document_id() -> None:
    document = make_document(
        make_block("Skills", DocumentBlockType.HEADING, 0),
        make_block("Python", DocumentBlockType.BULLET, 1),
    )

    result = ResumeStructureInterpreter().interpret(document)

    assert result.document_id == "resume-001"