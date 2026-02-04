import logging
from fastapi import Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from src.api.schemas import ErrorResponse

# Configure basic logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Set logging level to ERROR
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles FastAPI's HTTPException."""
    logger.error(f"HTTP Error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=str(exc.detail), error_code="HTTP_ERROR"
        ).model_dump(mode="json"),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic validation errors."""
    error_details = exc.errors()
    logger.error(f"Validation Error: {error_details}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            detail=str(error_details), error_code="VALIDATION_ERROR"
        ).model_dump(mode="json"),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handles SQLAlchemy-related database errors."""
    logger.exception("Database error occurred")  # Logs exception traceback
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="Database error occurred", error_code="DB_ERROR"
        ).model_dump(mode="json"),
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handles all other unhandled exceptions."""
    logger.exception("Unhandled application error")  # Logs exception traceback
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="Internal Server Error", error_code="INTERNAL_ERROR"
        ).model_dump(mode="json"),
    )
