from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence


class DimensionScore(BaseModel):
    """Score for an individual analysis dimension."""

    dimension: str
    score: float = Field(ge=0.0, le=100.0)
    weight: float = Field(ge=0.0, le=1.0)


class ScoreAdjustment(BaseModel):
    """A deterministic scoring adjustment."""

    reason: str
    value: float


class ScoringResult(BaseModel):
    """Canonical scoring output.

    Public scores are represented on a 0-100 scale.
    """

    overall_score: float = Field(ge=0.0, le=100.0)
    skill_score: float = Field(ge=0.0, le=100.0)
    required_skill_score: float = Field(ge=0.0, le=100.0)
    preferred_skill_score: float = Field(ge=0.0, le=100.0)
    experience_score: float = Field(ge=0.0, le=100.0)
    education_score: float = Field(ge=0.0, le=100.0)
    domain_score: float = Field(ge=0.0, le=100.0)

    dimension_scores: list[DimensionScore] = Field(default_factory=list)
    weights: dict[str, float] = Field(default_factory=dict)
    penalties: list[ScoreAdjustment] = Field(default_factory=list)
    bonuses: list[ScoreAdjustment] = Field(default_factory=list)

    confidence: Confidence | None = None
