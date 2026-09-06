from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class Skill(BaseModel):
    """Canonical normalized skill representation."""

    skill_id: str
    canonical_name: str
    display_name: str
    category: str | None = None
    subcategory: str | None = None
    aliases: list[str] = Field(default_factory=list)
    proficiency: str | None = None
    importance: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
