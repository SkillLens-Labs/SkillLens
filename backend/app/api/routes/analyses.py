from fastapi import APIRouter, File, UploadFile, status

from backend.app.core.exceptions import ApplicationError
from backend.app.schemas.responses import (
    AnalysisAcceptedResponse,
    AnalysisResponse,
    DeleteAnalysisResponse,
)

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post(
    "/resume",
    response_model=AnalysisAcceptedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def analyze_resume(
    resume: UploadFile = File(...),
) -> AnalysisAcceptedResponse:
    """Accept a resume for resume-only analysis."""

    raise ApplicationError(
        code="ANALYSIS_NOT_IMPLEMENTED",
        message="Resume analysis is not implemented in Phase 1.",
    )


@router.post(
    "/resume-jd",
    response_model=AnalysisAcceptedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def analyze_resume_jd(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...),
) -> AnalysisAcceptedResponse:
    """Accept a resume and job description for analysis."""

    raise ApplicationError(
        code="ANALYSIS_NOT_IMPLEMENTED",
        message="Resume + job-description analysis is not implemented in Phase 1.",
    )


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_analysis(analysis_id: str) -> AnalysisResponse:
    """Retrieve an analysis result."""

    raise ApplicationError(
        code="ANALYSIS_NOT_IMPLEMENTED",
        message="Analysis retrieval is not implemented in Phase 1.",
    )


@router.delete(
    "/{analysis_id}",
    response_model=DeleteAnalysisResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def delete_analysis(analysis_id: str) -> DeleteAnalysisResponse:
    """Delete an analysis result."""

    raise ApplicationError(
        code="ANALYSIS_NOT_IMPLEMENTED",
        message="Analysis deletion is not implemented in Phase 1.",
    )
