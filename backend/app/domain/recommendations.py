from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class RecommendationType(StrEnum):
    LEARNING = "learning"
    PROJECT = "project"
    CERTIFICATION = "certification"
    RESUME = "resume"
    CAREER = "career"


class Recommendation(BaseModel):
    """Canonical career or skill recommendation."""

    recommendation_id: str
    type: RecommendationType

    title: str
    target_skill: str | None = None

    priority: str
    rationale: str

    expected_impact: str | None = None
    effort: str | None = None

    evidence: list[Evidence] = Field(default_factory=list)
    related_gap_ids: list[str] = Field(default_factory=list)

    confidence: Confidence | None = None
