from typing import Any

from pydantic import BaseModel, Field


class AnalysisOptions(BaseModel):
    """Optional controls for an analysis request."""

    include_career_intelligence: bool = True
    include_recommendations: bool = True
    include_xai: bool = True


class ClientMetadata(BaseModel):
    """Optional metadata supplied by the client."""

    source: str | None = None
    session_id: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class ResumeAnalysisRequest(BaseModel):
    """Contract for a resume-only analysis request."""

    options: AnalysisOptions = Field(default_factory=AnalysisOptions)
    client_metadata: ClientMetadata | None = None


class ResumeJDAnalysisRequest(BaseModel):
    """Contract for a resume + job-description analysis request."""

    options: AnalysisOptions = Field(default_factory=AnalysisOptions)
    client_metadata: ClientMetadata | None = None
