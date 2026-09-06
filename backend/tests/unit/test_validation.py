from __future__ import annotations

from io import BytesIO

import pymupdf
import pytest
from docx import Document

from backend.app.core.exceptions import ApplicationError
from backend.app.infrastructure.parsers.models import DocumentType
from backend.app.infrastructure.parsers.validation import validate_document


PDF_CONTENT_TYPE = "application/pdf"

DOCX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "wordprocessingml.document"
)


def create_pdf() -> bytes:
    """Create a minimal valid PDF."""
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Validation test PDF",
        fontsize=12,
    )

    content = document.tobytes()
    document.close()

    return content


def create_docx() -> bytes:
    """Create a minimal valid DOCX."""
    document = Document()
    document.add_paragraph("Validation test DOCX")

    output = BytesIO()
    document.save(output)

    return output.getvalue()


def test_valid_pdf_is_accepted() -> None:
    content = create_pdf()

    result = validate_document(
        filename="resume.pdf",
        content=content,
        content_type=PDF_CONTENT_TYPE,
    )

    assert result.document_type == DocumentType.PDF
    assert result.filename == "resume.pdf"
    assert result.size_bytes == len(content)


def test_valid_docx_is_accepted() -> None:
    content = create_docx()

    result = validate_document(
        filename="resume.docx",
        content=content,
        content_type=DOCX_CONTENT_TYPE,
    )

    assert result.document_type == DocumentType.DOCX
    assert result.filename == "resume.docx"
    assert result.size_bytes == len(content)


def test_filename_is_normalized() -> None:
    content = create_pdf()

    result = validate_document(
        filename="  resume.PDF  ",
        content=content,
    )

    assert result.filename == "resume.PDF"
    assert result.document_type == DocumentType.PDF


def test_missing_filename_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="",
            content=create_pdf(),
        )

    assert exc_info.value.code == "DOCUMENT_FILENAME_REQUIRED"


def test_whitespace_filename_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="   ",
            content=create_pdf(),
        )

    assert exc_info.value.code == "DOCUMENT_FILENAME_REQUIRED"


def test_unsupported_extension_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.txt",
            content=b"some text",
        )

    assert exc_info.value.code == "UNSUPPORTED_DOCUMENT_TYPE"


def test_missing_extension_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume",
            content=create_pdf(),
        )

    assert exc_info.value.code == "UNSUPPORTED_DOCUMENT_TYPE"


def test_empty_content_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.pdf",
            content=b"",
        )

    assert exc_info.value.code == "EMPTY_DOCUMENT"


def test_pdf_with_wrong_binary_content_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.pdf",
            content=b"this-is-not-a-pdf",
        )

    assert exc_info.value.code == "DOCUMENT_CONTENT_MISMATCH"


def test_docx_with_wrong_binary_content_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.docx",
            content=b"this-is-not-a-docx",
        )

    assert exc_info.value.code == "DOCUMENT_CONTENT_MISMATCH"


def test_pdf_with_docx_content_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.pdf",
            content=create_docx(),
        )

    assert exc_info.value.code == "DOCUMENT_CONTENT_MISMATCH"


def test_docx_with_pdf_content_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.docx",
            content=create_pdf(),
        )

    assert exc_info.value.code == "DOCUMENT_CONTENT_MISMATCH"


def test_pdf_with_docx_mime_type_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.pdf",
            content=create_pdf(),
            content_type=DOCX_CONTENT_TYPE,
        )

    assert exc_info.value.code == "DOCUMENT_CONTENT_TYPE_MISMATCH"


def test_docx_with_pdf_mime_type_is_rejected() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.docx",
            content=create_docx(),
            content_type=PDF_CONTENT_TYPE,
        )

    assert exc_info.value.code == "DOCUMENT_CONTENT_TYPE_MISMATCH"


def test_pdf_with_correct_mime_type_and_parameters_is_accepted() -> None:
    content = create_pdf()

    result = validate_document(
        filename="resume.pdf",
        content=content,
        content_type="application/pdf; charset=binary",
    )

    assert result.document_type == DocumentType.PDF


def test_docx_with_correct_mime_type_and_parameters_is_accepted() -> None:
    content = create_docx()

    result = validate_document(
        filename="resume.docx",
        content=content,
        content_type=(
            DOCX_CONTENT_TYPE
            + "; charset=binary"
        ),
    )

    assert result.document_type == DocumentType.DOCX


def test_octet_stream_is_allowed_for_pdf() -> None:
    content = create_pdf()

    result = validate_document(
        filename="resume.pdf",
        content=content,
        content_type="application/octet-stream",
    )

    assert result.document_type == DocumentType.PDF


def test_octet_stream_is_allowed_for_docx() -> None:
    content = create_docx()

    result = validate_document(
        filename="resume.docx",
        content=content,
        content_type="application/octet-stream",
    )

    assert result.document_type == DocumentType.DOCX


def test_unknown_mime_type_is_rejected_for_pdf() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.pdf",
            content=create_pdf(),
            content_type="text/plain",
        )

    assert exc_info.value.code == "UNSUPPORTED_DOCUMENT_CONTENT_TYPE"


def test_unknown_mime_type_is_rejected_for_docx() -> None:
    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.docx",
            content=create_docx(),
            content_type="text/plain",
        )

    assert exc_info.value.code == "UNSUPPORTED_DOCUMENT_CONTENT_TYPE"


def test_oversized_document_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    class MockSettings:
        max_upload_size_mb = 1

    monkeypatch.setattr(
        "backend.app.infrastructure.parsers.validation.get_settings",
        lambda: MockSettings(),
    )

    oversized_content = b"x" * (1024 * 1024 + 1)

    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.pdf",
            content=oversized_content,
        )

    assert exc_info.value.code == "DOCUMENT_TOO_LARGE"


def test_docx_requires_valid_ooxml_container() -> None:
    # This starts like a ZIP file but does not contain the required
    # OOXML structures of a DOCX.
    fake_zip_content = b"PK\x03\x04not-a-real-docx"

    with pytest.raises(ApplicationError) as exc_info:
        validate_document(
            filename="resume.docx",
            content=fake_zip_content,
        )

    assert exc_info.value.code == "DOCUMENT_CONTENT_MISMATCH"