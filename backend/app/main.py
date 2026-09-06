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


@app.exception_handler(ApplicationError)
async def application_error_handler(
    request: Request,
    exc: ApplicationError,
) -> JSONResponse:
    """Convert internal application errors into the stable API error contract."""

    request_id = str(uuid4())

    error_response = ErrorResponse(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        field=exc.field,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=501,
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