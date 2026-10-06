"""
src/api/dependencies.py
FastAPI dependency injection providers for the inference engine and database repository.
"""

from fastapi import Request, HTTPException, status
from src.inference.engine import PartVisionInferenceEngine
from src.database.repository import PartVisionRepository


def get_inference_engine(request: Request) -> PartVisionInferenceEngine:
    """
    Retrieves the singleton PartVisionInferenceEngine instance from application state.
    Raises HTTP 500 if the engine was not initialized during startup.
    """
    engine = getattr(request.app.state, "inference_engine", None)
    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference engine is not initialized on the application state.",
        )
    return engine


def get_repository(request: Request) -> PartVisionRepository:
    """
    Retrieves the PartVisionRepository instance from application state.
    Raises HTTP 500 if the database repository was not initialized during startup.
    """
    repo = getattr(request.app.state, "repository", None)
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database repository is not initialized on the application state.",
        )
    return repo
