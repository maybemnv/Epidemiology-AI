"""
API Dependencies

Shared dependencies, utilities, and dependency injection for FastAPI routes.
"""

from pathlib import Path
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.service import ModelService
from ..core.config import get_settings
from ..database.core import get_db
from ..database.models import User
from .schemas import TokenData

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


# ============================================================================
# Model Service Dependency
# ============================================================================

# Global model service instance
_model_service: ModelService = None


def get_model_path() -> Path:
    """Get the path to the trained model file"""
    # Model is stored in project root /models folder
    return (
        Path(__file__).parent.parent.parent / "models" / "dengue_outbreak_predictor.pkl"
    )


def init_model_service() -> ModelService:
    """Initialize the global model service"""
    global _model_service
    if _model_service is None:
        model_path = get_model_path()
        _model_service = ModelService(str(model_path))
    return _model_service


def get_model_service() -> ModelService:
    """
    Dependency injection for model service.

    Usage:
        @router.get("/predict")
        async def predict(service: ModelService = Depends(get_model_service)):
            ...
    """
    if _model_service is None:
        init_model_service()
    return _model_service


# ============================================================================
# Utility Functions
# ============================================================================


def validate_prediction_input(
    temp_avg: float, temp_min: float, temp_max: float
) -> bool:
    """Validate that temperature values are logically consistent"""
    return temp_min <= temp_avg <= temp_max


# ============================================================================
# Auth Dependencies
# ============================================================================


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    return user
