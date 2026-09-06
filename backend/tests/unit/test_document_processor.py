from __future__ import annotations

from io import BytesIO

import pymupdf
import pytest
from docx import Document

from backend.app.core.exceptions import ApplicationError
from backend.app.infrastructure.parsers.document_processor import (
    DocumentProcessor,
)
from backend.app.infrastructure.parsers.models import DocumentType


def create_pdf(text: str) -> bytes:
    """Create a minimal in-memory PDF."""
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text(
        (72, 72),
        text,
        fontsize=12,
    )

    content = document.tobytes()
    document.close()

    return content


def create_docx(text: str) -> bytes:
    """Create a minimal in-memory DOCX."""
    document = Document()
    document.add_paragraph(text)

    output = BytesIO()
    document.save(output)

    return output.getvalue()


def test_processor_parses_pdf() -> None:
    processor = DocumentProcessor()

    content = create_pdf("PDF document content")

    result = processor.process(
        filename="resume.pdf",
        content=content,
        content_type="application/pdf",
        document_id="pdf-001",
    )

    assert result.document_id == "pdf-001"
    assert result.document_type == DocumentType.PDF
    assert "PDF document content" in result.text


def test_processor_parses_docx() -> None:
    processor = DocumentProcessor()

    content = create_docx("DOCX document content")

    result = processor.process(
        filename="resume.docx",
        content=content,
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        document_id="docx-001",
    )

    assert result.document_id == "docx-001"
    assert result.document_type == DocumentType.DOCX
    assert "DOCX document content" in result.text


def test_processor_generates_document_id_when_not_provided() -> None:
    processor = DocumentProcessor()

    content = create_pdf("Generated ID test")

    result = processor.process(
        filename="resume.pdf",
        content=content,
    )

    assert result.document_id
    assert isinstance(result.document_id, str)


def test_processor_preserves_supplied_document_id() -> None:
    processor = DocumentProcessor()

    content = create_docx("Document ID test")

    result = processor.process(
        filename="resume.docx",
        content=content,
        document_id="custom-document-id",
    )

    assert result.document_id == "custom-document-id"


def test_processor_rejects_unsupported_extension() -> None:
    processor = DocumentProcessor()

    with pytest.raises(ApplicationError) as exc_info:
        processor.process(
            filename="resume.txt",
            content=b"plain text",
        )

    assert exc_info.value.code == "UNSUPPORTED_DOCUMENT_TYPE"


def test_processor_rejects_empty_content() -> None:
    processor = DocumentProcessor()

    with pytest.raises(ApplicationError) as exc_info:
        processor.process(
            filename="resume.pdf",
            content=b"",
        )

    assert exc_info.value.code == "EMPTY_DOCUMENT"


def test_processor_rejects_invalid_pdf() -> None:
    processor = DocumentProcessor()

    with pytest.raises(ApplicationError) as exc_info:
        processor.process(
            filename="resume.pdf",
            content=b"not-a-real-pdf",
        )

    assert exc_info.value.code == "DOCUMENT_CONTENT_MISMATCH"


def test_processor_rejects_invalid_docx() -> None:
    processor = DocumentProcessor()

    with pytest.raises(ApplicationError) as exc_info:
        processor.process(
            filename="resume.docx",
            content=b"not-a-real-docx",
        )

    assert exc_info.value.code == "DOCUMENT_CONTENT_MISMATCH"


def test_supports_pdf() -> None:
    processor = DocumentProcessor()

    assert processor.supports("resume.pdf") is True
    assert processor.supports("RESUME.PDF") is True


def test_supports_docx() -> None:
    processor = DocumentProcessor()

    assert processor.supports("resume.docx") is True
    assert processor.supports("RESUME.DOCX") is True


def test_does_not_support_other_extensions() -> None:
    processor = DocumentProcessor()

    assert processor.supports("resume.txt") is False
    assert processor.supports("resume.doc") is False
    assert processor.supports("resume.xlsx") is False


def test_supported_types() -> None:
    processor = DocumentProcessor()

    supported = processor.supported_types()

    assert DocumentType.PDF in supported
    assert DocumentType.DOCX in supported
    assert len(supported) == 2