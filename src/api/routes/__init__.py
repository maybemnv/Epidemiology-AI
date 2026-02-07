"""
Routes Package

Aggregates all route modules for easy importing.
"""

from fastapi import APIRouter

from .health import router as health_router
from .predictions import router as predictions_router
from .model import router as model_router
from .auth import router as auth_router
from .ingestion import router as ingestion_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(predictions_router)
api_router.include_router(model_router)
api_router.include_router(ingestion_router, prefix="/ingest", tags=["Data Ingestion"])

__all__ = ["health_router", "api_router"]
