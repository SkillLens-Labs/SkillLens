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


class ScoreContribution(BaseModel):
    """Deterministic contribution of one scoring component.

    Contribution is represented on a normalized 0-1 internal scale.
    """

    contribution_id: str
    dimension: str
    source_type: str
    source_id: str
    score: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0)
    contribution: float
    rationale: str
    requirement_type: str | None = None


class ScoringResult(BaseModel):
    """Canonical deterministic scoring output.

    Public scores are represented on a 0-100 scale.
    Internal contribution values remain normalized to 0-1.
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

    contributions: list[ScoreContribution] = Field(default_factory=list)

    penalties: list[ScoreAdjustment] = Field(default_factory=list)
    bonuses: list[ScoreAdjustment] = Field(default_factory=list)

    confidence: Confidence | None = None
