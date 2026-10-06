"""
src/api/routes/health.py
Health check and system status monitoring route.
"""

from fastapi import APIRouter, Request
from src.api.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health and component status",
    description="Returns service availability, model readiness, and database connectivity.",
)
async def health_check(request: Request) -> HealthResponse:
    """Verifies that the inference engine and database connection are active."""
    engine = getattr(request.app.state, "inference_engine", None)
    model_loaded = engine is not None and getattr(engine, "model", None) is not None

    repo = getattr(request.app.state, "repository", None)
    db_connected = False
    if repo is not None:
        try:
            parts = repo.get_all_parts()
            db_connected = len(parts) == 19
        except Exception:
            db_connected = False

    status_str = "healthy" if (model_loaded and db_connected) else "degraded"

    return HealthResponse(
        status=status_str,
        service="PartVision AI API",
        version="0.4.0",
        model="partvision_v3_yolo11n_seg",
        model_loaded=model_loaded,
        database_connected=db_connected,
    )
