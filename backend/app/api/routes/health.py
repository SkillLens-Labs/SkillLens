from fastapi import APIRouter

from backend.app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return basic application health information."""

    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }
