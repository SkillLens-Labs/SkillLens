from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class CareerSeniorityLevel(StrEnum):
    """Controlled seniority classification for career intelligence."""

    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    UNKNOWN = "unknown"


class CareerDirection(StrEnum):
    """Career direction classification based on available evidence."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class RoleFit(BaseModel):
    """Deterministic generalized fit assessment for a career role."""

    role: str
    fit_score: float = Field(ge=0.0, le=100.0)
    direction: CareerDirection
    rationale: str
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence


class SkillPriority(BaseModel):
    """Existing compatibility model retained for the canonical career contract."""

    skill_id: str
    skill_name: str
    priority: str
    rationale: str | None = None


class CareerDirectionResult(BaseModel):
    """Evidence-backed career direction."""

    role: str
    direction: CareerDirection
    fit_score: float = Field(ge=0.0, le=100.0)
    rationale: str
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence


class CareerIntelligence(BaseModel):
    """Canonical deterministic Phase 7 career-intelligence result."""

    inferred_profile: str | None = None

    experience_level: CareerSeniorityLevel = CareerSeniorityLevel.UNKNOWN
    seniority_confidence: Confidence
    seniority_evidence: list[Evidence] = Field(default_factory=list)
    seniority_rationale: str

    primary_domains: list[str] = Field(default_factory=list)
    secondary_domains: list[str] = Field(default_factory=list)

    strengths: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    transferable_skills: list[str] = Field(default_factory=list)

    career_directions: list[CareerDirectionResult] = Field(default_factory=list)

    potential_roles: list[str] = Field(default_factory=list)
    role_fit: list[RoleFit] = Field(default_factory=list)

    career_signals: list[str] = Field(default_factory=list)

    # Retained for backward compatibility with the existing domain contract.
    transition_analysis: str | None = None
    skill_priorities: list[SkillPriority] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)

    confidence: Confidence

    taxonomy_version: str
    engine_version: str
