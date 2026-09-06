from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Stable error response returned by the SkillLens API."""

    code: str
    message: str
    details: Any | None = None
    field: str | None = None
    request_id: str
