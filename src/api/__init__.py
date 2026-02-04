"""
API Package

Exports all API components.
"""

from .routes import health_router, api_router
from .schemas import (
    PredictionRequest,
    PredictionResponse,
    ModelStatsResponse,
    HealthResponse,
    RootResponse,
)
from .dependencies import get_model_service, init_model_service

__all__ = [
    "health_router",
    "api_router",
    "PredictionRequest",
    "PredictionResponse",
    "ModelStatsResponse",
    "HealthResponse",
    "RootResponse",
    "get_model_service",
    "init_model_service",
]
