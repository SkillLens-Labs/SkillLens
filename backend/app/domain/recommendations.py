from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class RecommendationType(StrEnum):
    """Controlled recommendation categories."""

    LEARNING = "learning"
    PROJECT = "project"
    CERTIFICATION = "certification"
    RESUME = "resume"
    CAREER = "career"
    JOB_ALIGNMENT = "job_alignment"


class RecommendationPriority(StrEnum):
    """Controlled recommendation priority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationEffort(StrEnum):
    """Estimated implementation effort."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecommendationImpact(StrEnum):
    """Expected impact on candidate readiness."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recommendation(BaseModel):
    """
    Canonical evidence-backed recommendation.

    Recommendations are produced by the deterministic Recommendation
    Intelligence layer. Optional LLM providers may later improve only
    natural-language explanations and must not determine analytical
    outcomes such as matching, gap classification, priority, impact,
    confidence, or ranking.
    """

    recommendation_id: str

    type: RecommendationType

    title: str

    target_skill: str | None = None

    priority: RecommendationPriority

    rationale: str

    expected_impact: RecommendationImpact | None = None

    effort: RecommendationEffort | None = None

    evidence: list[Evidence] = Field(default_factory=list)

    related_gap_ids: list[str] = Field(default_factory=list)

    confidence: Confidence | None = None

    # Deterministic ranking score used internally and exposed for
    # transparency/debugging. This is not the same as confidence.
    priority_score: float = Field(default=0.0, ge=0.0, le=100.0)

    # Optional numeric estimate describing expected candidate-readiness
    # improvement. This is deterministic and must not be confused with
    # recommendation confidence.
    impact_score: float = Field(default=0.0, ge=0.0, le=100.0)

    # Identifies the deterministic engine responsible for the
    # recommendation. Useful for reproducibility and future versioning.
    source_engine: str = "recommendation-intelligence-v1"
