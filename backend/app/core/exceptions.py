from dataclasses import dataclass
from typing import Any


@dataclass
class ApplicationError(Exception):
    """Base application error used internally by the backend."""

    code: str
    message: str
    details: Any | None = None
    field: str | None = None

    def __str__(self) -> str:
        return self.message
