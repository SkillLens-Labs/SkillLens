from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.domain.confidence import Confidence
from backend.app.domain.evidence import Evidence


class LanguageIssueType(StrEnum):
    """Controlled categories for resume language-quality findings."""

    SPELLING = "spelling"
    GRAMMAR = "grammar"
    WORDING = "wording"
    TERMINOLOGY = "terminology"
    FORMATTING = "formatting"


class LanguageIssueSeverity(StrEnum):
    """Severity of a language-quality finding."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LanguageIssue(BaseModel):
    """Evidence-backed language-quality finding."""

    issue_id: str
    issue_type: LanguageIssueType
    severity: LanguageIssueSeverity
    title: str
    explanation: str
    recommendation: str | None = None
    original_text: str | None = None
    suggested_text: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence


class AIAuthorshipHeuristic(BaseModel):
    """
    Conservative writing-style estimate.

    This is explicitly a heuristic and must never be presented as factual
    detection of AI authorship.
    """

    score: float = Field(ge=0.0, le=100.0)
    level: str
    signals: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "This is a heuristic writing-style estimate, not proof of AI authorship."
    )


class ResumeLanguageQualityResult(BaseModel):
    """Canonical language-quality analysis result."""

    overall_score: float = Field(ge=0.0, le=100.0)
    issues: list[LanguageIssue] = Field(default_factory=list)
    confidence: Confidence
    authorship_heuristic: AIAuthorshipHeuristic
    warnings: list[str] = Field(default_factory=list)
