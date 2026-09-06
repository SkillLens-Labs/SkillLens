from pydantic import BaseModel

from backend.app.domain.analysis import AnalysisResult


class AnalysisResponse(BaseModel):
    """Stable API response containing the canonical analysis result."""

    data: AnalysisResult


class AnalysisAcceptedResponse(BaseModel):
    """Response returned when an analysis has been accepted for processing."""

    analysis_id: str
    status: str
    message: str


class DeleteAnalysisResponse(BaseModel):
    """Response returned after an analysis is deleted."""

    analysis_id: str
    deleted: bool
    message: str
