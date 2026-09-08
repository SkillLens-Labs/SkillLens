from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class MatchRelationship(StrEnum):
    EXACT = "exact"
    STRONG_SEMANTIC = "strong_semantic"
    PARTIAL = "partial"
    RELATED = "related"
    UNMATCHED = "unmatched"


class JobRequirementType(StrEnum):
    """Classification of a job requirement by hiring preference."""

    REQUIRED = "required"
    PREFERRED = "preferred"


class JobRequirementCategory(StrEnum):
    """Canonical category for a structured job requirement."""

    SKILL = "skill"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATION = "certification"


class RequirementMatchStatus(StrEnum):
    """Evidence-aware alignment state for a job requirement."""

    MATCHED = "matched"
    PARTIAL = "partial"
    UNMATCHED = "unmatched"
    UNKNOWN = "unknown"


class JobRequirement(BaseModel):
    """Canonical structured representation of one job requirement."""

    requirement_id: str
    text: str
    requirement_type: JobRequirementType
    category: JobRequirementCategory
    skill_id: str | None = None
    canonical_name: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class RequirementAlignment(BaseModel):
    """Evidence-aware alignment between a job requirement and a resume."""

    requirement_id: str
    status: RequirementMatchStatus
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence | None = None
    rationale: str | None = None


class SkillMatch(BaseModel):
    """Canonical relationship between a resume skill and job skill."""

    resume_skill_id: str
    job_skill_id: str
    relationship: MatchRelationship
    similarity: float = Field(ge=0.0, le=1.0)
    confidence: Confidence | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    rationale: str | None = None


class MatchingResult(BaseModel):
    """Canonical Phase 5 matching result without scoring or XAI."""

    skill_matches: list[SkillMatch] = Field(default_factory=list)
    requirement_alignments: list[RequirementAlignment] = Field(default_factory=list)
    confidence: Confidence | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
