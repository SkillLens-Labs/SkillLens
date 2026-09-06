from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence


class RoleFit(BaseModel):
    """Fit assessment for a potential career role."""

    role: str
    fit_score: float = Field(ge=0.0, le=100.0)
    rationale: str | None = None
    confidence: Confidence | None = None


class SkillPriority(BaseModel):
    """Prioritized skill for career development."""

    skill_id: str
    skill_name: str
    priority: str
    rationale: str | None = None


class CareerIntelligence(BaseModel):
    """Canonical career intelligence output."""

    inferred_profile: str | None = None
    experience_level: str | None = None

    primary_domains: list[str] = Field(default_factory=list)
    secondary_domains: list[str] = Field(default_factory=list)

    strengths: list[str] = Field(default_factory=list)
    career_signals: list[str] = Field(default_factory=list)

    potential_roles: list[str] = Field(default_factory=list)
    role_fit: list[RoleFit] = Field(default_factory=list)

    transition_analysis: str | None = None
    skill_priorities: list[SkillPriority] = Field(default_factory=list)

    risks: list[str] = Field(default_factory=list)
    confidence: Confidence | None = None
