from __future__ import annotations

from io import BytesIO

import pymupdf
from docx import Document

from backend.app.infrastructure.parsers.docx_parser import DOCXParser
from backend.app.infrastructure.parsers.models import (
    DocumentBlockType,
    DocumentType,
    ParsedDocument,
)
from backend.app.infrastructure.parsers.pdf_parser import PDFParser


def create_pdf(pages: list[list[str]]) -> bytes:
    document = pymupdf.open()

    for page_lines in pages:
        page = document.new_page()
        y_position = 72

        for line in page_lines:
            page.insert_text(
                (72, y_position),
                line,
                fontsize=12,
            )
            y_position += 20

    content = document.tobytes()
    document.close()

    return content


def create_docx(
    paragraphs: list[tuple[str, str | None]],
) -> bytes:
    document = Document()

    for text, style in paragraphs:
        document.add_paragraph(text, style=style)

    output = BytesIO()
    document.save(output)

    return output.getvalue()


def assert_normalized_document_contract(
    document: ParsedDocument,
    expected_type: DocumentType,
    expected_id: str,
) -> None:
    assert isinstance(document, ParsedDocument)
    assert document.document_id == expected_id
    assert document.document_type == expected_type
    assert isinstance(document.blocks, list)
    assert isinstance(document.metadata, dict)

    for block in document.blocks:
        assert block.text.strip()
        assert isinstance(block.block_type, DocumentBlockType)
        assert block.source is not None


def test_pdf_produces_normalized_parsed_document() -> None:
    parser = PDFParser()

    content = create_pdf(
        [
            ["Candidate Name", "Software Engineer"],
            ["Professional Experience", "Python Developer"],
        ]
    )

    result = parser.parse(
        content=content,
        document_id="normalized-pdf",
    )

    assert_normalized_document_contract(
        result,
        DocumentType.PDF,
        "normalized-pdf",
    )


def test_docx_produces_normalized_parsed_document() -> None:
    parser = DOCXParser()

    content = create_docx(
        [
            ("Candidate Name", None),
            ("Professional Experience", "Heading 1"),
            ("Python Developer", None),
        ]
    )

    result = parser.parse(
        content=content,
        document_id="normalized-docx",
    )

    assert_normalized_document_contract(
        result,
        DocumentType.DOCX,
        "normalized-docx",
    )


def test_pdf_block_order_is_deterministic_across_pages() -> None:
    parser = PDFParser()

    content = create_pdf(
        [
            ["Page 1 - First", "Page 1 - Second"],
            ["Page 2 - First", "Page 2 - Second"],
        ]
    )

    result = parser.parse(
        content=content,
        document_id="pdf-order",
    )

    texts = [block.text for block in result.blocks]

    assert texts == [
        "Page 1 - First",
        "Page 1 - Second",
        "Page 2 - First",
        "Page 2 - Second",
    ]


def test_pdf_provenance_matches_block_order() -> None:
    parser = PDFParser()

    content = create_pdf(
        [
            ["Page 1 - First", "Page 1 - Second"],
            ["Page 2 - First"],
        ]
    )

    result = parser.parse(
        content=content,
        document_id="pdf-provenance-order",
    )

    assert result.blocks

    previous_page = 0
    previous_block_index = -1

    for block in result.blocks:
        source = block.source

        assert source.page_number is not None
        assert source.block_index is not None

        if source.page_number == previous_page:
            assert source.block_index > previous_block_index
        else:
            assert source.page_number > previous_page
            previous_block_index = -1

        previous_page = source.page_number
        previous_block_index = source.block_index


def test_docx_paragraph_provenance_matches_document_order() -> None:
    parser = DOCXParser()

    content = create_docx(
        [
            ("First", None),
            ("Second", None),
            ("Third", None),
        ]
    )

    result = parser.parse(
        content=content,
        document_id="docx-provenance-order",
    )

    paragraph_blocks = [
        block
        for block in result.blocks
        if block.source.paragraph_index is not None
    ]

    assert [block.text for block in paragraph_blocks] == [
        "First",
        "Second",
        "Third",
    ]

    paragraph_indices = [
        block.source.paragraph_index
        for block in paragraph_blocks
    ]

    assert paragraph_indices == sorted(paragraph_indices)


def test_normalized_text_is_reconstructable_from_blocks() -> None:
    parser = PDFParser()

    content = create_pdf(
        [
            ["First block", "Second block"],
            ["Third block"],
        ]
    )

    result = parser.parse(
        content=content,
        document_id="text-reconstruction",
    )

    expected_text = "\n".join(
        block.text
        for block in result.blocks
        if block.text.strip()
    )

    assert result.text == expected_text


def test_empty_pdf_still_obeys_normalized_contract() -> None:
    document = pymupdf.open()
    document.new_page()

    content = document.tobytes()
    document.close()

    result = PDFParser().parse(
        content=content,
        document_id="empty-pdf-contract",
    )

    assert_normalized_document_contract(
        result,
        DocumentType.PDF,
        "empty-pdf-contract",
    )

    assert result.blocks == []
    assert result.text == ""


def test_empty_docx_still_obeys_normalized_contract() -> None:
    content = create_docx([])

    result = DOCXParser().parse(
        content=content,
        document_id="empty-docx-contract",
    )

    assert_normalized_document_contract(
        result,
        DocumentType.DOCX,
        "empty-docx-contract",
    )

    assert result.blocks == []
    assert result.text == ""