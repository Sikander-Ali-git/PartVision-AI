"""
src/api/app.py
FastAPI application factory and lifecycle management for PartVision AI (Milestone 7).
"""

import time
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.inference.engine import PartVisionInferenceEngine
from src.database.repository import PartVisionRepository
from src.database.connection import DEFAULT_DB_PATH
from src.api.routes import health, analysis, parts, vehicles, compatibility

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("partvision.api")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "partvision_v3_yolo11n_seg_best.pt"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    Loads and warms up the frozen YOLO11n-seg model once at startup and connects
    to the SQLite compatibility database.
    """
    logger.info("Initializing PartVision AI API backend...")

    # 1. Verify and initialize Database Repository
    db_path = DEFAULT_DB_PATH
    if not db_path.exists():
        logger.error(f"Compatibility database not found at {db_path}!")
        raise RuntimeError(f"Database file missing: {db_path}")

    logger.info(f"Connecting to compatibility database: {db_path}")
    repo = PartVisionRepository(db_path=db_path)
    try:
        parts_count = len(repo.get_all_parts())
        logger.info(f"Database initialized: {parts_count} canonical parts accessible.")
    except Exception as exc:
        logger.error(f"Database connection failed: {exc}")
        raise RuntimeError(f"Failed to access database: {exc}") from exc

    app.state.repository = repo

    # 2. Verify and load Frozen YOLO11n-seg Model
    model_path = DEFAULT_MODEL_PATH
    if not model_path.exists():
        logger.error(f"Model checkpoint not found at {model_path}!")
        raise RuntimeError(f"Model weights file missing: {model_path}")

    logger.info(f"Loading frozen PartVision V3 YOLO11n-seg checkpoint: {model_path}")
    t0 = time.perf_counter()
    try:
        engine = PartVisionInferenceEngine(
            model_path=model_path,
            device="auto",
            verbose=False,
        )
        load_duration_ms = (time.perf_counter() - t0) * 1000.0
        logger.info(
            f"Inference engine successfully loaded in {load_duration_ms:.2f} ms "
            f"(device: {engine.device})."
        )
    except Exception as exc:
        logger.error(f"Inference engine initialization failed: {exc}")
        raise RuntimeError(f"Failed to initialize inference engine: {exc}") from exc

    app.state.inference_engine = engine
    app.state.model_load_duration_ms = load_duration_ms

    yield

    # Clean shutdown
    logger.info("Shutting down PartVision AI API backend...")


def create_app() -> FastAPI:
    """Creates and configures the FastAPI application instance."""
    app = FastAPI(
        title="PartVision AI API",
        version="0.4.0",
        description="AI-powered automotive spare-part identification and compatibility lookup.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS for local frontend development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------------
    # Exception Handlers
    # -------------------------------------------------------------------------
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Uniform JSON formatting for HTTP exceptions."""
        error_type = "NotFoundError" if exc.status_code == 404 else "ClientError"
        if exc.status_code == 413:
            error_type = "PayloadTooLarge"
        elif exc.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE:
            error_type = "UnsupportedMediaType"
        elif exc.status_code >= 500:
            error_type = "InternalServerError"

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": error_type,
                "detail": str(exc.detail),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Format request validation failures cleanly."""
        errors = exc.errors()
        error_msg = errors[0]["msg"] if errors else "Invalid request data."
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "detail": error_msg,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Prevents leaking internal tracebacks to clients."""
        logger.exception(f"Unhandled exception processing request {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "detail": "An unexpected error occurred while processing the request.",
            },
        )

    # -------------------------------------------------------------------------
    # Register Route Handlers
    # -------------------------------------------------------------------------
    app.include_router(health.router)
    app.include_router(analysis.router)
    app.include_router(parts.router)
    app.include_router(vehicles.router)
    app.include_router(compatibility.router)

    return app


# Default application instance for Uvicorn
app = create_app()
