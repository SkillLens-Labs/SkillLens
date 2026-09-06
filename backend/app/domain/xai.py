from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class SkillExplanation(BaseModel):
    """Explanation associated with an individual skill result."""

    skill_id: str
    explanation: str
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence | None = None


class EvidenceMapEntry(BaseModel):
    """Maps an analytical result to supporting evidence."""

    result_type: str
    result_id: str
    evidence: list[Evidence] = Field(default_factory=list)


class XAIResult(BaseModel):
    """Canonical explainability output.

    XAI explains existing analytical results and does not recalculate them.
    """

    overall_explanation: str | None = None
    score_explanation: str | None = None

    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)

    matched_skill_explanations: list[SkillExplanation] = Field(default_factory=list)
    missing_skill_explanations: list[SkillExplanation] = Field(default_factory=list)
    partial_match_explanations: list[SkillExplanation] = Field(default_factory=list)

    evidence_map: list[EvidenceMapEntry] = Field(default_factory=list)

    confidence: Confidence | None = None
