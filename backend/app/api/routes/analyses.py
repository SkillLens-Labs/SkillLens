import json

from fastapi import APIRouter, File, Form, UploadFile, status

from backend.app.core.exceptions import ApplicationError
from backend.app.orchestration.analysis_orchestrator import AnalysisOrchestrator
from backend.app.orchestration.concrete_analysis_orchestrator import (
    ConcreteAnalysisOrchestrator,
)
from backend.app.schemas.requests import (
    ClientMetadata,
    ResumeAnalysisRequest,
    ResumeDocumentInput,
)
from backend.app.schemas.responses import (
    AnalysisAcceptedResponse,
    AnalysisResponse,
    DeleteAnalysisResponse,
)

router = APIRouter(prefix="/analyses", tags=["analyses"])

_orchestrator: AnalysisOrchestrator = ConcreteAnalysisOrchestrator()


def _parse_request_payload(
    options: str | None,
    client_metadata: str | None,
) -> ResumeAnalysisRequest:
    parsed_options = None
    parsed_metadata = None

    if options is not None:
        try:
            parsed_options = json.loads(options)
        except json.JSONDecodeError as exc:
            raise ApplicationError(
                code="INVALID_ANALYSIS_OPTIONS",
                message="The options field must contain valid JSON.",
                field="options",
            ) from exc

    if client_metadata is not None:
        try:
            parsed_metadata = json.loads(client_metadata)
        except json.JSONDecodeError as exc:
            raise ApplicationError(
                code="INVALID_CLIENT_METADATA",
                message="The client_metadata field must contain valid JSON.",
                field="client_metadata",
            ) from exc

    try:
        payload = {}
        if parsed_options is not None:
            payload["options"] = parsed_options
        if parsed_metadata is not None:
            payload["client_metadata"] = parsed_metadata

        return ResumeAnalysisRequest.model_validate(payload)
    except ValueError as exc:
        raise ApplicationError(
            code="INVALID_ANALYSIS_REQUEST",
            message="The analysis request contains invalid fields.",
        ) from exc


@router.post(
    "/resume",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_resume(
    resume: UploadFile = File(...),
    options: str | None = Form(default=None),
    client_metadata: str | None = Form(default=None),
) -> AnalysisResponse:
    """Run synchronous resume-only analysis."""

    content = await resume.read()

    request = _parse_request_payload(
        options=options,
        client_metadata=client_metadata,
    )

    document_input = ResumeDocumentInput(
        filename=resume.filename or "",
        content=content,
        content_type=resume.content_type,
    )

    result = _orchestrator.analyze_resume(
        document_input,
        request,
    )

    return AnalysisResponse(data=result)


@router.post(
    "/resume-jd",
    response_model=AnalysisAcceptedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def analyze_resume_jd(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...),
) -> AnalysisAcceptedResponse:
    """Resume + job-description analysis remains outside Phase 4."""

    raise ApplicationError(
        code="ANALYSIS_NOT_IMPLEMENTED",
        message="Resume + job-description analysis is not implemented in Phase 4.",
    )


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def get_analysis(analysis_id: str) -> AnalysisResponse:
    """Retrieve a completed analysis result."""

    result = _orchestrator.get_analysis(analysis_id)

    if result is None:
        raise ApplicationError(
            code="ANALYSIS_NOT_FOUND",
            message=f"Analysis '{analysis_id}' was not found.",
            field="analysis_id",
        )

    return AnalysisResponse(data=result)


@router.delete(
    "/{analysis_id}",
    response_model=DeleteAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_analysis(analysis_id: str) -> DeleteAnalysisResponse:
    """Delete an existing analysis result."""

    deleted = _orchestrator.delete_analysis(analysis_id)

    if not deleted:
        raise ApplicationError(
            code="ANALYSIS_NOT_FOUND",
            message=f"Analysis '{analysis_id}' was not found.",
            field="analysis_id",
        )

    return DeleteAnalysisResponse(
        analysis_id=analysis_id,
        deleted=True,
        message="Analysis deleted successfully.",
    )
