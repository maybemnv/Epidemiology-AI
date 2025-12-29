"""
Epidemiology AI - Main Application Entry Point

FastAPI application for Disease Outbreak Early Warning System.
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import from src package
from src.api import health_router, api_router, init_model_service


def create_app() -> FastAPI:
    """Application factory - creates and configures the FastAPI app"""
    
    app = FastAPI(
        title="Epidemiology AI API",
        description="Disease Outbreak Early Warning System - Predict dengue outbreaks using ML",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router)  # Root level: /, /health
    app.include_router(api_router)     # API level: /api/v1/...

    return app


# Create app instance
app = create_app()


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    print("=" * 70)
    print(" " * 15 + "EPIDEMIOLOGY AI API")
    print(" " * 10 + "Disease Outbreak Early Warning System")
    print("=" * 70)
    
    # Initialize model service
    service = init_model_service()
    
    if service.is_model_loaded():
        stats = service.get_model_statistics()
        print(f"✓ Model loaded successfully")
        print(f"  - Features: {stats.get('features_count', 'N/A')}")
        print(f"  - Threshold: {stats.get('outbreak_threshold', 'N/A')}")
        if stats.get('performance_metrics'):
            print(f"  - R² Score: {stats['performance_metrics'].get('R2', 'N/A'):.3f}")
    else:
        print("⚠ Model not loaded!")
        print("  Run notebook to train model:")
        print("  > jupyter notebook notebooks/dengue_outbreak_prediction.ipynb")
    
    print("=" * 70)
    print("API Endpoints:")
    print("  - Health:     GET  /health")
    print("  - Predict:    POST /api/v1/predict")
    print("  - Model Info: GET  /api/v1/model/stats")
    print("  - Reload:     POST /api/v1/model/reload")
    print("  - Docs:       GET  /docs")
    print("=" * 70)


if __name__ == "__main__":
    import uvicorn
    print("\nStarting Epidemiology AI API Server...")
    print("Documentation: http://localhost:8000/docs\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
