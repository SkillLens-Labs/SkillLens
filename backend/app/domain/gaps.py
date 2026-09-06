from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class SkillGap(BaseModel):
    """Canonical representation of an identified skill gap."""

    gap_id: str
    target_skill_id: str
    target_skill_name: str
    gap_type: str
    severity: str | None = None
    rationale: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence | None = None


class SkillAnalysis(BaseModel):
    """Canonical skill-analysis result."""

    extracted_skills: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    partial_matches: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    transferable_skills: list[str] = Field(default_factory=list)
    gaps: list[SkillGap] = Field(default_factory=list)
