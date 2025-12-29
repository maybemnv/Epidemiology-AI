"""
Health Check Routes

Endpoints for monitoring API health and status.
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from ..schemas import HealthResponse, RootResponse
from ..dependencies import get_model_service
from ...models.service import ModelService

router = APIRouter(tags=["Health"])


@router.get("/", response_model=RootResponse)
async def root(service: ModelService = Depends(get_model_service)):
    """
    Root endpoint - API information and available endpoints
    """
    return RootResponse(
        message="Epidemiology AI - Disease Outbreak Early Warning System",
        status="active",
        version="1.0.0",
        model_loaded=service.is_model_loaded(),
        endpoints={
            "docs": "/docs",
            "health": "/health",
            "predict": "/api/v1/predict",
            "model_stats": "/api/v1/model/stats",
            "model_reload": "/api/v1/model/reload"
        }
    )


@router.get("/health", response_model=HealthResponse)
async def health_check(service: ModelService = Depends(get_model_service)):
    """
    Health check endpoint for monitoring and load balancers
    """
    model_loaded = service.is_model_loaded()
    
    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        timestamp=datetime.now(),
        model_status="loaded" if model_loaded else "not_loaded",
        message="All systems operational" if model_loaded else "Model not loaded - predictions unavailable"
    )
