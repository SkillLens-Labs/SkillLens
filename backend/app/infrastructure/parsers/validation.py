from __future__ import annotations

from pathlib import Path
from zipfile import BadZipFile, ZipFile
from io import BytesIO

from backend.app.core.config import get_settings
from backend.app.core.exceptions import ApplicationError
from backend.app.infrastructure.parsers.models import (
    DocumentType,
    DocumentValidationResult,
)


SUPPORTED_EXTENSIONS: dict[str, DocumentType] = {
    ".pdf": DocumentType.PDF,
    ".docx": DocumentType.DOCX,
}

PDF_CONTENT_TYPES = {
    "application/pdf",
}

DOCX_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

PDF_SIGNATURE = b"%PDF-"
ZIP_SIGNATURE = b"PK"


def validate_document(
    filename: str,
    content: bytes,
    content_type: str | None = None,
) -> DocumentValidationResult:
    """
    Validate a supported document before parsing.

    Validation responsibilities:
    - filename presence
    - supported extension
    - non-empty content
    - configured maximum size
    - extension/content consistency
    - known MIME/content-type consistency

    Parsing and document-structure validation remain the responsibility
    of the individual document parsers.
    """
    if not filename or not filename.strip():
        raise ApplicationError(
            code="DOCUMENT_FILENAME_REQUIRED",
            message="A document filename is required.",
        )

    normalized_filename = filename.strip()
    extension = Path(normalized_filename).suffix.lower()

    document_type = SUPPORTED_EXTENSIONS.get(extension)

    if document_type is None:
        raise ApplicationError(
            code="UNSUPPORTED_DOCUMENT_TYPE",
            message=(
                f"Unsupported document type '{extension or 'unknown'}'. "
                "Supported types are PDF and DOCX."
            ),
        )

    if not content:
        raise ApplicationError(
            code="EMPTY_DOCUMENT",
            message="The uploaded document is empty.",
        )

    settings = get_settings()
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    size_bytes = len(content)

    if size_bytes > max_size_bytes:
        raise ApplicationError(
            code="DOCUMENT_TOO_LARGE",
            message=(
                f"Document exceeds the maximum allowed size of "
                f"{settings.max_upload_size_mb} MB."
            ),
            details={
                "size_bytes": size_bytes,
                "max_size_bytes": max_size_bytes,
            },
        )

    _validate_content_signature(
        document_type=document_type,
        content=content,
    )

    _validate_content_type(
        document_type=document_type,
        content_type=content_type,
    )

    return DocumentValidationResult(
        document_type=document_type,
        filename=normalized_filename,
        size_bytes=size_bytes,
    )


def _validate_content_signature(
    document_type: DocumentType,
    content: bytes,
) -> None:
    """Validate that the file bytes match the declared extension."""

    if document_type == DocumentType.PDF:
        if not content.startswith(PDF_SIGNATURE):
            raise ApplicationError(
                code="DOCUMENT_CONTENT_MISMATCH",
                message="The file extension is PDF, but the content is not a PDF.",
            )

        return

    if document_type == DocumentType.DOCX:
        if not content.startswith(ZIP_SIGNATURE):
            raise ApplicationError(
                code="DOCUMENT_CONTENT_MISMATCH",
                message="The file extension is DOCX, but the content is not a DOCX.",
            )

        if not _is_valid_docx_container(content):
            raise ApplicationError(
                code="DOCUMENT_CONTENT_MISMATCH",
                message="The file extension is DOCX, but the content is not a valid DOCX container.",
            )


def _validate_content_type(
    document_type: DocumentType,
    content_type: str | None,
) -> None:
    """
    Validate a supplied MIME type.

    Unknown/omitted content types are allowed because clients and browsers
    are not always reliable when setting MIME metadata.

    A known MIME type that contradicts the extension is rejected.
    """
    if content_type is None:
        return

    normalized_content_type = content_type.split(";", 1)[0].strip().lower()

    if not normalized_content_type:
        return

    if document_type == DocumentType.PDF:
        if normalized_content_type in DOCX_CONTENT_TYPES:
            raise ApplicationError(
                code="DOCUMENT_CONTENT_TYPE_MISMATCH",
                message="The filename indicates PDF, but the content type indicates DOCX.",
            )

        if (
            normalized_content_type != "application/octet-stream"
            and normalized_content_type not in PDF_CONTENT_TYPES
        ):
            raise ApplicationError(
                code="UNSUPPORTED_DOCUMENT_CONTENT_TYPE",
                message=(
                    f"Unsupported content type '{normalized_content_type}' "
                    "for a PDF document."
                ),
            )

        return

    if document_type == DocumentType.DOCX:
        if normalized_content_type in PDF_CONTENT_TYPES:
            raise ApplicationError(
                code="DOCUMENT_CONTENT_TYPE_MISMATCH",
                message="The filename indicates DOCX, but the content type indicates PDF.",
            )

        if (
            normalized_content_type != "application/octet-stream"
            and normalized_content_type not in DOCX_CONTENT_TYPES
        ):
            raise ApplicationError(
                code="UNSUPPORTED_DOCUMENT_CONTENT_TYPE",
                message=(
                    f"Unsupported content type '{normalized_content_type}' "
                    "for a DOCX document."
                ),
            )


def _is_valid_docx_container(content: bytes) -> bool:
    """
    Verify that the ZIP container contains the minimum OOXML structures
    expected from a DOCX document.

    This intentionally does not replace python-docx validation.
    """
    try:
        with ZipFile(BytesIO(content)) as archive:
            names = set(archive.namelist())

            return (
                "[Content_Types].xml" in names
                and "word/document.xml" in names
            )

    except (BadZipFile, OSError, ValueError):
        return False