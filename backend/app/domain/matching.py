from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class MatchRelationship(StrEnum):
    EXACT = "exact"
    STRONG_SEMANTIC = "strong_semantic"
    PARTIAL = "partial"
    RELATED = "related"
    UNMATCHED = "unmatched"


class SkillMatch(BaseModel):
    """Canonical relationship between a resume skill and job skill."""

    resume_skill_id: str
    job_skill_id: str
    relationship: MatchRelationship
    similarity: float = Field(ge=0.0, le=1.0)
    confidence: Confidence | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    rationale: str | None = None
