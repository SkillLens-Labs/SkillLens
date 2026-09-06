from __future__ import annotations

from abc import ABC, abstractmethod

from backend.app.infrastructure.parsers.models import (
    DocumentType,
    ParsedDocument,
)


class DocumentParser(ABC):
    """Contract implemented by supported document parsers."""

    document_type: DocumentType

    @abstractmethod
    def parse(
        self,
        content: bytes,
        *,
        document_id: str,
    ) -> ParsedDocument:
        """Parse document bytes into a structurally preserved representation."""
        raise NotImplementedError
