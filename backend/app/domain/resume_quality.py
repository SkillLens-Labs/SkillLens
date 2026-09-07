from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class ResumeQualitySeverity(StrEnum):
    """Severity of a resume-quality finding."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResumeQualityDimension(StrEnum):
    """Canonical dimensions used by resume-quality analysis."""

    STRUCTURE = "structure"
    COMPLETENESS = "completeness"
    SKILLS_PRESENTATION = "skills_presentation"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    PROJECTS = "projects"
    CONTENT_QUALITY = "content_quality"
    CONSISTENCY = "consistency"


class ResumeQualityFinding(BaseModel):
    """Deterministic finding produced by resume-quality analysis."""

    finding_id: str
    category: ResumeQualityDimension
    severity: ResumeQualitySeverity
    title: str
    explanation: str
    recommendation: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence


class ResumeQualityDimensionScore(BaseModel):
    """Score for one resume-quality dimension."""

    dimension: ResumeQualityDimension
    score: float = Field(ge=0.0, le=100.0)
    weight: float = Field(ge=0.0, le=1.0)


class ResumeQualityResult(BaseModel):
    """Canonical resume-quality analysis result."""

    overall_score: float = Field(ge=0.0, le=100.0)
    dimension_scores: list[ResumeQualityDimensionScore] = Field(
        default_factory=list
    )
    findings: list[ResumeQualityFinding] = Field(default_factory=list)
    confidence: Confidence
    warnings: list[str] = Field(default_factory=list)
