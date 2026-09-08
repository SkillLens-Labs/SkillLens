from backend.app.analysis.jd_structure import (
    JDSectionType,
    JDStructureInterpreter,
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
        document_id="job-001",
        document_type=DocumentType.DOCX,
        blocks=list(blocks),
    )


def test_interpreter_detects_common_jd_sections() -> None:
    document = make_document(
        make_block("Data Engineer", DocumentBlockType.PARAGRAPH, 0),
        make_block("About the Role", DocumentBlockType.HEADING, 1),
        make_block("Build data systems.", DocumentBlockType.PARAGRAPH, 2),
        make_block("Responsibilities", DocumentBlockType.HEADING, 3),
        make_block("Build pipelines.", DocumentBlockType.BULLET, 4),
        make_block("Required Qualifications", DocumentBlockType.HEADING, 5),
        make_block("Python and SQL.", DocumentBlockType.BULLET, 6),
        make_block("Preferred Qualifications", DocumentBlockType.HEADING, 7),
        make_block("Cloud experience.", DocumentBlockType.BULLET, 8),
    )

    result = JDStructureInterpreter().interpret(document)

    assert [section.section_type for section in result.sections] == [
        JDSectionType.HEADER,
        JDSectionType.SUMMARY,
        JDSectionType.RESPONSIBILITIES,
        JDSectionType.REQUIRED_QUALIFICATIONS,
        JDSectionType.PREFERRED_QUALIFICATIONS,
    ]


def test_interpreter_handles_heading_aliases_and_colons() -> None:
    document = make_document(
        make_block("WHAT YOU'LL DO:", DocumentBlockType.HEADING, 0),
        make_block("Build APIs.", DocumentBlockType.BULLET, 1),
        make_block("MINIMUM QUALIFICATIONS", DocumentBlockType.HEADING, 2),
        make_block("Python.", DocumentBlockType.BULLET, 3),
        make_block("NICE TO HAVE:", DocumentBlockType.HEADING, 4),
        make_block("AWS.", DocumentBlockType.BULLET, 5),
    )

    result = JDStructureInterpreter().interpret(document)

    assert [
        section.section_type for section in result.sections
    ] == [
        JDSectionType.RESPONSIBILITIES,
        JDSectionType.REQUIRED_QUALIFICATIONS,
        JDSectionType.PREFERRED_QUALIFICATIONS,
    ]


def test_unknown_heading_is_preserved_as_unknown() -> None:
    document = make_document(
        make_block("Data Engineer", DocumentBlockType.PARAGRAPH, 0),
        make_block("Benefits", DocumentBlockType.HEADING, 1),
        make_block("Health insurance.", DocumentBlockType.PARAGRAPH, 2),
    )

    result = JDStructureInterpreter().interpret(document)

    assert result.sections[0].section_type == JDSectionType.HEADER
    assert result.sections[1].section_type == JDSectionType.UNKNOWN
    assert result.sections[1].heading == "Benefits"


def test_non_heading_blocks_do_not_start_new_sections() -> None:
    document = make_document(
        make_block("Data Engineer", DocumentBlockType.PARAGRAPH, 0),
        make_block("Python", DocumentBlockType.BULLET, 1),
        make_block("SQL", DocumentBlockType.PARAGRAPH, 2),
    )

    result = JDStructureInterpreter().interpret(document)

    assert len(result.sections) == 1
    assert result.sections[0].section_type == JDSectionType.HEADER
    assert [
        block.text for block in result.sections[0].blocks
    ] == [
        "Data Engineer",
        "Python",
        "SQL",
    ]


def test_section_blocks_preserve_original_order() -> None:
    document = make_document(
        make_block("Responsibilities", DocumentBlockType.HEADING, 0),
        make_block("Build APIs.", DocumentBlockType.BULLET, 1),
        make_block("Write tests.", DocumentBlockType.BULLET, 2),
        make_block("Review code.", DocumentBlockType.BULLET, 3),
    )

    result = JDStructureInterpreter().interpret(document)

    responsibilities = result.sections_of(
        JDSectionType.RESPONSIBILITIES
    )[0]

    assert [block.text for block in responsibilities.blocks] == [
        "Build APIs.",
        "Write tests.",
        "Review code.",
    ]


def test_interpreter_preserves_document_id() -> None:
    document = make_document(
        make_block("Skills", DocumentBlockType.HEADING, 0),
        make_block("Python", DocumentBlockType.BULLET, 1),
    )

    result = JDStructureInterpreter().interpret(document)

    assert result.document_id == "job-001"