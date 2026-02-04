from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.exceptions import (  # Relative import
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
)
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

# Import from current package's api
from .api.routes import health_router, api_router  # Adjusted import


def create_app() -> FastAPI:
    """Application factory - creates and configures the FastAPI app"""

    app = FastAPI(
        title="Epidemiology AI API",
        description=(
            "Disease Outbreak Early Warning System - "
            "Predict dengue outbreaks using ML"
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Register custom exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

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
    app.include_router(api_router)  # API level: /api/v1/...
    return app


# Removed `app = create_app()` and `if __name__ == "__main__":`
# block as this will be a module
# The main.py at root will handle app creation and running
