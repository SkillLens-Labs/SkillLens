from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class SkillGap(BaseModel):
    """Canonical representation of a requirement-linked skill gap."""

    gap_id: str
    requirement_id: str
    requirement_type: str
    target_skill_id: str
    target_skill_name: str

    # Phase 5 alignment status preserved as the authoritative classification.
    # Expected values: matched, partial, unmatched, unknown.
    match_status: str

    # Gap classification is only populated for non-matched outcomes.
    # Expected values: partial, unmatched, unknown.
    gap_type: str

    severity: str | None = None

    # Existing Phase 5 matching strength is preserved separately from confidence.
    similarity: float | None = Field(default=None, ge=0.0, le=1.0)

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
