from __future__ import annotations

from uuid import uuid4

from backend.app.infrastructure.parsers.base import DocumentParser
from backend.app.infrastructure.parsers.docx_parser import DOCXParser
from backend.app.infrastructure.parsers.models import (
    DocumentType,
    ParsedDocument,
)
from backend.app.infrastructure.parsers.pdf_parser import PDFParser
from backend.app.infrastructure.parsers.validation import validate_document


class DocumentProcessor:
    """
    Application-facing facade for document validation and parsing.

    The processor deliberately hides individual parser implementations from
    higher layers such as the analysis orchestrator.
    """

    def __init__(
        self,
        parsers: list[DocumentParser] | None = None,
    ) -> None:
        configured_parsers = parsers or [
            PDFParser(),
            DOCXParser(),
        ]

        self._parsers: dict[DocumentType, DocumentParser] = {
            parser.document_type: parser
            for parser in configured_parsers
        }

    def process(
        self,
        filename: str,
        content: bytes,
        content_type: str | None = None,
        document_id: str | None = None,
    ) -> ParsedDocument:
        """
        Validate and parse a document.

        If no document_id is supplied, a new UUID is generated.
        """
        validation = validate_document(
            filename=filename,
            content=content,
            content_type=content_type,
        )

        parser = self._parsers.get(validation.document_type)

        if parser is None:
            # This should normally be unreachable because validation only
            # accepts supported document types.
            from backend.app.core.exceptions import ApplicationError

            raise ApplicationError(
                code="DOCUMENT_PARSER_NOT_AVAILABLE",
                message=(
                    f"No parser is registered for "
                    f"{validation.document_type.value} documents."
                ),
            )

        resolved_document_id = document_id or str(uuid4())

        return parser.parse(
            content=content,
            document_id=resolved_document_id,
        )

    def supports(self, filename: str) -> bool:
        """
        Return whether the filename has a supported document extension.

        This method does not validate file contents.
        """
        from pathlib import Path

        extension = Path(filename).suffix.lower()

        return extension in {
            ".pdf",
            ".docx",
        }

    def supported_types(self) -> tuple[DocumentType, ...]:
        """Return the document types currently supported by the processor."""
        return tuple(self._parsers.keys())