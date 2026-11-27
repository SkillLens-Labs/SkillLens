from __future__ import annotations

from collections import Counter
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

# Common resume/JD section titles. A standalone short block matching one of
# these is treated as a heading even when PDF font metadata is unavailable.
_HEADING_ALIASES = frozenset(
    {
        "contact", "contact information", "summary", "professional summary",
        "profile", "professional profile", "objective", "career objective",
        "experience", "work experience", "professional experience",
        "employment history", "career history", "education",
        "education and training", "skills", "key skills", "core skills",
        "technical skills", "skill summary", "technologies",
        "technical competencies", "projects", "key projects", "certifications",
        "certificates", "licenses and certifications", "achievements",
        "achievements and awards", "awards", "accomplishments", "languages",
        "interests", "hobbies", "publications", "volunteer experience",
        "volunteering", "activities", "responsibilities", "requirements",
        "qualifications", "required qualifications", "minimum qualifications",
        "preferred qualifications", "basic qualifications", "must have",
        "nice to have", "nice-to-have", "desired qualifications",
        "about the role", "about this role", "job summary", "position summary",
        "job overview", "overview", "job description", "role and responsibilities",
        "roles and responsibilities", "key responsibilities", "duties",
        "job duties", "benefits", "experience requirements",
        "education requirements", "educational qualifications", "experience & education",
    }
)

_BULLET_PREFIXES = (
    "•", "●", "○", "▪", "▫", "‣", "·", "- ", "* ", "– ", "— ",
)


class PDFParser(DocumentParser):
    """Parser for extracting structured text from PDF documents."""

    document_type = DocumentType.PDF

    def parse(self, content: bytes, document_id: str) -> ParsedDocument:
        """
        Parse PDF bytes into a ParsedDocument.

        Unlike the V1 parser, blocks carry font-derived heading signals so
        downstream structure interpreters can reconstruct resume/JD sections
        from PDFs, not only from DOCX.
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
            pages_data: list[tuple[int, dict[str, Any]]] = []
            size_counter: Counter[float] = Counter()

            for page_number, page in enumerate(document, start=1):
                page_data = page.get_text("dict")
                pages_data.append((page_number, page_data))

                for raw_block in page_data.get("blocks", []):
                    if raw_block.get("type") != 0:
                        continue  # skip image blocks
                    for line in raw_block.get("lines", []):
                        for span in line.get("spans", []):
                            if str(span.get("text", "")).strip():
                                size_counter[
                                    round(float(span.get("size", 0) or 0), 1)
                                ] += 1

            body_size = (
                max(size_counter.items(), key=lambda item: item[1])[0]
                if size_counter
                else 10.0
            )

            blocks: list[DocumentBlock] = []

            for page_number, page_data in pages_data:
                for block_index, raw_block in enumerate(
                    page_data.get("blocks", [])
                ):
                    if raw_block.get("type") != 0:
                        continue

                    text, span_info = self._block_text(raw_block)

                    if not text:
                        continue

                    bbox = raw_block.get("bbox", (0.0, 0.0, 0.0, 0.0))

                    blocks.append(
                        DocumentBlock(
                            text=text,
                            block_type=self._classify_block(
                                text, span_info, body_size,
                            ),
                            source=SourceLocation(
                                page_number=page_number,
                                block_index=block_index,
                                bbox=tuple(float(v) for v in bbox),
                            ),
                            style_name=span_info.get("font"),
                            section=None,
                            metadata={
                                "page_number": page_number,
                                "font_size": span_info.get("size"),
                                "bold": span_info.get("bold", False),
                                "body_font_size": body_size,
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
                    "body_font_size": body_size,
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
    def _block_text(raw_block: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Extract block text and dominant font signals from a dict block."""
        lines_text: list[str] = []
        max_size = 0.0
        bold = False
        font: str | None = None

        for line in raw_block.get("lines", []):
            line_parts: list[str] = []
            for span in line.get("spans", []):
                span_text = str(span.get("text", ""))
                if not span_text.strip():
                    continue
                line_parts.append(span_text)

                size = float(span.get("size", 0) or 0)
                span_font = str(span.get("font", ""))
                span_bold = bool(span.get("flags", 0) & 16) or "bold" in span_font.lower()

                if size >= max_size:
                    max_size = size
                    font = span_font
                if span_bold:
                    bold = True

            if line_parts:
                lines_text.append(" ".join(line_parts).strip())

        return "\n".join(lines_text).strip(), {
            "size": max_size,
            "bold": bold,
            "font": font,
        }

    @staticmethod
    def _classify_block(
        text: str,
        span_info: dict[str, Any],
        body_size: float,
    ) -> DocumentBlockType:
        """Classify a PDF block using font metadata plus text heuristics."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if not lines:
            return DocumentBlockType.PARAGRAPH

        first_line = lines[0]

        if first_line.startswith(_BULLET_PREFIXES):
            return DocumentBlockType.BULLET

        normalized = " ".join(first_line.lower().split())
        normalized = normalized.rstrip(":").strip().rstrip("–—-").strip()

        if normalized in _HEADING_ALIASES:
            return DocumentBlockType.HEADING

        size = float(span_info.get("size") or 0.0)
        bold = bool(span_info.get("bold"))
        is_short = len(first_line) <= 80 and len(lines) <= 2

        if is_short and size >= body_size + 1.0:
            return DocumentBlockType.HEADING

        # Bold alone (same size as body) is not enough: project titles and
        # degree lines are commonly bold. Require ALL CAPS as well.
        if is_short and bold and first_line.isupper():
            return DocumentBlockType.HEADING

        return DocumentBlockType.PARAGRAPH
