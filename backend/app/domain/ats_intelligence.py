from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class ATSIntelligenceSeverity(StrEnum):
    """Severity of an ATS-intelligence finding."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ATSIntelligenceDimension(StrEnum):
    """Canonical dimensions used by ATS-intelligence analysis."""

    MACHINE_READABILITY = "machine_readability"
    SECTION_DETECTABILITY = "section_detectability"
    TEXT_EXTRACTION = "text_extraction"
    HEADING_CLARITY = "heading_clarity"
    SKILL_DETECTABILITY = "skill_detectability"
    CONTACT_DETECTABILITY = "contact_detectability"
    FORMATTING_RISK = "formatting_risk"
    CONTENT_REDUNDANCY = "content_redundancy"
    STANDARD_INFORMATION = "standard_information"


class ATSIntelligenceFinding(BaseModel):
    """Deterministic finding produced by ATS-intelligence analysis."""

    finding_id: str
    category: ATSIntelligenceDimension
    severity: ATSIntelligenceSeverity
    title: str
    explanation: str
    recommendation: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence


class ATSIntelligenceDimensionScore(BaseModel):
    """Score for one ATS-intelligence dimension."""

    dimension: ATSIntelligenceDimension
    score: float = Field(ge=0.0, le=100.0)
    weight: float = Field(ge=0.0, le=1.0)


class ATSIntelligenceResult(BaseModel):
    """Canonical ATS-intelligence analysis result."""

    overall_score: float = Field(ge=0.0, le=100.0)
    dimension_scores: list[ATSIntelligenceDimensionScore] = Field(
        default_factory=list
    )
    findings: list[ATSIntelligenceFinding] = Field(default_factory=list)
    confidence: Confidence
    warnings: list[str] = Field(default_factory=list)
