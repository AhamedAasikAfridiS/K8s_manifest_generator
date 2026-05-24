"""Health endpoints."""

from fastapi import APIRouter

from app.config import get_settings
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    llm_mode = "mock" if settings.should_use_mock else "openai"
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        llm_mode=llm_mode,
    )
