from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DocumentType(StrEnum):
    PDF = "pdf"
    DOCX = "docx"


class DocumentBlockType(StrEnum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    BULLET = "bullet"
    TABLE_CELL = "table_cell"


@dataclass(frozen=True)
class SourceLocation:
    """Location of extracted content in the original document."""

    page_number: int | None = None
    paragraph_index: int | None = None
    table_index: int | None = None
    row_index: int | None = None
    column_index: int | None = None
    block_index: int | None = None
    bbox: tuple[float, float, float, float] | None = None


@dataclass
class DocumentBlock:
    """A structurally preserved piece of extracted document content."""

    text: str
    block_type: DocumentBlockType
    source: SourceLocation
    style_name: str | None = None
    section: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDocument:
    """Normalized structural representation of a supported document."""

    document_id: str
    document_type: DocumentType
    blocks: list[DocumentBlock] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        """Return document text without discarding the underlying blocks."""
        return "\n".join(
            block.text for block in self.blocks if block.text.strip()
        )


@dataclass(frozen=True)
class DocumentValidationResult:
    """Result of validating an uploaded document."""

    document_type: DocumentType
    filename: str
    size_bytes: int
