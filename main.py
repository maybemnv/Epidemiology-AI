from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import from src package
from src.api import health_router, api_router
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi import Request, status, HTTPException
from src.api.schemas import ErrorResponse


def create_app() -> FastAPI:
    """Application factory - creates and configures the FastAPI app"""

    app = FastAPI(
        title="Epidemiology AI API",
        description="Disease Outbreak Early Warning System - Predict dengue outbreaks using ML",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                detail=str(exc.detail), error_code="HTTP_ERROR"
            ).model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                detail=str(exc.errors()), error_code="VALIDATION_ERROR"
            ).model_dump(mode="json"),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        # Log the error in a real app
        print(f"DB Error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                detail="Database error occurred", error_code="DB_ERROR"
            ).model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        # Log the error
        print(f"Unhandled Error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                detail="Internal Server Error", error_code="INTERNAL_ERROR"
            ).model_dump(mode="json"),
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
    app.include_router(api_router)  # API level: /api/v1/...
    return app


# Create app instance
app = create_app()
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
