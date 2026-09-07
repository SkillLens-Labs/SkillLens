from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.api.routes.analyses import router as analyses_router
from backend.app.api.routes.health import router as health_router
from backend.app.core.config import settings
from backend.app.core.exceptions import ApplicationError
from backend.app.core.logging import configure_logging
from backend.app.schemas.errors import ErrorResponse

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


def _application_error_status(code: str) -> int:
    if code in {
        "ANALYSIS_NOT_FOUND",
    }:
        return 404

    if code in {
        "DOCUMENT_TOO_LARGE",
        "FILE_TOO_LARGE",
    }:
        return 413

    if code in {
        "ANALYSIS_NOT_IMPLEMENTED",
    }:
        return 501

    if code in {
        "UNSUPPORTED_DOCUMENT_TYPE",
        "EMPTY_DOCUMENT",
        "UNSUPPORTED_DOCUMENT_CONTENT_TYPE",
        "DOCUMENT_CONTENT_MISMATCH",
        "DOCUMENT_CONTENT_TYPE_MISMATCH",
    }:
        return 400
    if code.startswith("DOCUMENT_") or code.startswith("INVALID_"):
        return 400

    return 500


@app.exception_handler(ApplicationError)
async def application_error_handler(
    request: Request,
    exc: ApplicationError,
) -> JSONResponse:
    """Convert application errors into the stable API error contract."""

    request_id = str(uuid4())

    error_response = ErrorResponse(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        field=exc.field,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=_application_error_status(exc.code),
        content=error_response.model_dump(mode="json"),
    )


app.include_router(
    health_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    analyses_router,
    prefix=settings.api_v1_prefix,
)
