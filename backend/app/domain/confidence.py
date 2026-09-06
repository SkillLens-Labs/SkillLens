from enum import StrEnum

from pydantic import BaseModel, Field


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Confidence(BaseModel):
    """Canonical confidence representation used across SkillLens."""

    score: float = Field(ge=0.0, le=1.0)
    level: ConfidenceLevel
    components: dict[str, float] = Field(default_factory=dict)
    rationale: str | None = None
