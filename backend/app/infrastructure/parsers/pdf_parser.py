from __future__ import annotations

from typing import Any

import pymupdf

from backend.app.core.exceptions import ApplicationError
from backend.app.infrastructure.parsers.base import DocumentParser
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    DocumentType,
    ParsedDocument,
    SourceLocation,
)


class PDFParser(DocumentParser):
    """Parser for extracting structured text from PDF documents."""

    document_type = DocumentType.PDF

    def parse(self, content: bytes, document_id: str) -> ParsedDocument:
        """
        Parse PDF bytes into a ParsedDocument.

        Text blocks retain their page and bounding-box provenance so that
        downstream processing can trace extracted text back to the source PDF.
        """
        if not content:
            raise ApplicationError(
                code="EMPTY_DOCUMENT",
                message="The PDF document is empty.",
            )

        try:
            document = pymupdf.open(stream=content, filetype="pdf")
        except Exception as exc:
            raise ApplicationError(
                code="INVALID_PDF_DOCUMENT",
                message="The uploaded file is not a valid PDF document.",
                details=str(exc),
            ) from exc

        try:
            blocks: list[DocumentBlock] = []

            for page_number, page in enumerate(document, start=1):
                page_blocks = page.get_text("blocks")

                for block_index, raw_block in enumerate(page_blocks):
                    if len(raw_block) < 5:
                        continue

                    x0, y0, x1, y1, text = raw_block[:5]

                    if not isinstance(text, str):
                        continue

                    text = text.strip()

                    if not text:
                        continue

                    block_type = self._classify_block(text)

                    source = SourceLocation(
                        page_number=page_number,
                        block_index=block_index,
                        bbox=(float(x0), float(y0), float(x1), float(y1)),
                    )

                    blocks.append(
                        DocumentBlock(
                            text=text,
                            block_type=block_type,
                            source=source,
                            style_name=None,
                            section=None,
                            metadata={
                                "page_number": page_number,
                            },
                        )
                    )

            return ParsedDocument(
                document_id=document_id,
                document_type=DocumentType.PDF,
                blocks=blocks,
                metadata={
                    "page_count": len(document),
                    "parser": "PyMuPDF",
                    "parser_version": pymupdf.VersionBind,
                },
            )

        except ApplicationError:
            raise

        except Exception as exc:
            raise ApplicationError(
                code="PDF_PARSE_FAILED",
                message="Failed to parse the PDF document.",
                details=str(exc),
            ) from exc

        finally:
            document.close()

    @staticmethod
    def _classify_block(text: str) -> DocumentBlockType:
        """
        Classify a PDF text block using conservative document-level heuristics.

        PDF text extraction does not reliably expose semantic paragraph/heading
        types, so classification remains intentionally lightweight.
        """
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if not lines:
            return DocumentBlockType.PARAGRAPH

        first_line = lines[0]

        bullet_prefixes = (
            "•",
            "●",
            "○",
            "▪",
            "▫",
            "‣",
            "- ",
            "* ",
            "– ",
            "— ",
        )

        if first_line.startswith(bullet_prefixes):
            return DocumentBlockType.BULLET

        return DocumentBlockType.PARAGRAPH