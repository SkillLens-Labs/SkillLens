from __future__ import annotations

import pymupdf
import pytest

from backend.app.core.exceptions import ApplicationError
from backend.app.infrastructure.parsers.models import (
    DocumentBlockType,
    DocumentType,
)
from backend.app.infrastructure.parsers.pdf_parser import PDFParser


def create_pdf(pages: list[list[str]]) -> bytes:
    """Create an in-memory PDF for testing."""
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


def test_parse_single_page_pdf() -> None:
    parser = PDFParser()

    content = create_pdf(
        [
            [
                "John Doe",
                "Python Developer",
                "Experienced software engineer.",
            ]
        ]
    )

    result = parser.parse(
        content=content,
        document_id="doc-001",
    )

    assert result.document_id == "doc-001"
    assert result.document_type == DocumentType.PDF
    assert len(result.blocks) > 0

    extracted_text = result.text

    assert "John Doe" in extracted_text
    assert "Python Developer" in extracted_text
    assert "Experienced software engineer." in extracted_text


def test_parse_multi_page_pdf() -> None:
    parser = PDFParser()

    content = create_pdf(
        [
            [
                "Page one",
                "Candidate information",
            ],
            [
                "Page two",
                "Professional experience",
            ],
            [
                "Page three",
                "Education",
            ],
        ]
    )

    result = parser.parse(
        content=content,
        document_id="doc-multi-page",
    )

    assert result.metadata["page_count"] == 3
    assert len(result.blocks) >= 3

    page_numbers = {
        block.source.page_number
        for block in result.blocks
    }

    assert page_numbers == {1, 2, 3}

    assert "Page one" in result.text
    assert "Page two" in result.text
    assert "Page three" in result.text


def test_pdf_block_provenance_is_preserved() -> None:
    parser = PDFParser()

    content = create_pdf(
        [
            [
                "Candidate Name",
                "Software Engineer",
            ]
        ]
    )

    result = parser.parse(
        content=content,
        document_id="doc-provenance",
    )

    assert result.blocks

    first_block = result.blocks[0]

    assert first_block.source.page_number == 1
    assert first_block.source.block_index is not None
    assert first_block.source.bbox is not None

    assert len(first_block.source.bbox) == 4

    x0, y0, x1, y1 = first_block.source.bbox

    assert x1 >= x0
    assert y1 >= y0


def test_whitespace_only_blocks_are_not_returned() -> None:
    document = pymupdf.open()
    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Valid text",
        fontsize=12,
    )

    page.insert_text(
        (72, 100),
        "     ",
        fontsize=12,
    )

    content = document.tobytes()
    document.close()

    parser = PDFParser()

    result = parser.parse(
        content=content,
        document_id="doc-whitespace",
    )

    assert result.blocks

    for block in result.blocks:
        assert block.text.strip() != ""

    assert "Valid text" in result.text


def test_empty_text_pdf_returns_no_blocks() -> None:
    parser = PDFParser()

    document = pymupdf.open()
    document.new_page()

    content = document.tobytes()
    document.close()

    result = parser.parse(
        content=content,
        document_id="doc-empty",
    )

    assert result.document_type == DocumentType.PDF
    assert result.document_id == "doc-empty"
    assert result.blocks == []
    assert result.text == ""


def test_corrupted_pdf_raises_application_error() -> None:
    parser = PDFParser()

    corrupted_content = b"%PDF-this-is-not-a-valid-pdf"

    with pytest.raises(ApplicationError) as exc_info:
        parser.parse(
            content=corrupted_content,
            document_id="doc-corrupted",
        )

    assert exc_info.value.code == "INVALID_PDF_DOCUMENT"


def test_empty_content_raises_application_error() -> None:
    parser = PDFParser()

    with pytest.raises(ApplicationError) as exc_info:
        parser.parse(
            content=b"",
            document_id="doc-empty-content",
        )

    assert exc_info.value.code == "EMPTY_DOCUMENT"