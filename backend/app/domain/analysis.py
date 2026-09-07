from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.domain.ats_intelligence import ATSIntelligenceResult
from backend.app.domain.career import CareerIntelligence
from backend.app.domain.gaps import SkillAnalysis
from backend.app.domain.job import JobProfile
from backend.app.domain.recommendations import Recommendation
from backend.app.domain.resume import ResumeProfile
from backend.app.domain.resume_quality import ResumeQualityResult
from backend.app.domain.scoring import ScoringResult
from backend.app.domain.xai import XAIResult


class AnalysisMode(StrEnum):
    RESUME_ONLY = "resume_only"
    RESUME_JD = "resume_jd"


class AnalysisStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisInput(BaseModel):
    """References the documents used for an analysis."""

    resume_document_id: str
    job_description_document_id: str | None = None


class AnalysisMetadata(BaseModel):
    """Metadata describing how an analysis was produced."""

    engine_versions: dict[str, str] = Field(default_factory=dict)
    processing_time_ms: int | None = Field(default=None, ge=0)
    warnings: list[str] = Field(default_factory=list)
    extra: dict[str, object] = Field(default_factory=dict)


class AnalysisResult(BaseModel):
    """Canonical single source of truth for SkillLens analysis results."""

    analysis_id: str
    schema_version: str = "1.0.0"

    analysis_mode: AnalysisMode
    status: AnalysisStatus

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    input: AnalysisInput

    resume_profile: ResumeProfile
    job_profile: JobProfile | None = None

    skill_analysis: SkillAnalysis = Field(default_factory=SkillAnalysis)
    resume_quality: ResumeQualityResult | None = None
    ats_intelligence: ATSIntelligenceResult | None = None

    scoring: ScoringResult | None = None
    xai: XAIResult | None = None
    career_intelligence: CareerIntelligence | None = None

    recommendations: list[Recommendation] = Field(default_factory=list)

    metadata: AnalysisMetadata = Field(default_factory=AnalysisMetadata)
