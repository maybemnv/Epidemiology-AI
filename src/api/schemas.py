"""
Pydantic Schemas for API Request/Response Models

All data models are defined here for consistency and reusability.
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime

# ============================================================================
# Prediction Schemas
# ============================================================================


class PredictionRequest(BaseModel):
    """Request model for outbreak prediction"""

    temp_avg: float = Field(..., description="Average temperature in °C", ge=-50, le=60)
    temp_min: float = Field(..., description="Minimum temperature in °C", ge=-50, le=60)
    temp_max: float = Field(..., description="Maximum temperature in °C", ge=-50, le=60)
    precipitation_mm: float = Field(..., description="Precipitation in mm", ge=0)
    humidity_percent: float = Field(
        ..., description="Relative humidity %", ge=0, le=100
    )
    weekofyear: int = Field(..., description="Week number of year", ge=1, le=53)
    previous_cases: List[int] = Field(
        ...,
        min_length=1,
        max_length=4,
        description="Case counts from previous 1-4 weeks",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "temp_avg": 27.5,
                "temp_min": 22.0,
                "temp_max": 33.0,
                "precipitation_mm": 45.2,
                "humidity_percent": 78.5,
                "weekofyear": 24,
                "previous_cases": [12, 15, 18, 22],
            }
        }
    )


class PredictionResponse(BaseModel):
    """Response model for outbreak prediction"""

    predicted_cases: float = Field(..., description="Predicted number of cases")
    risk_level: str = Field(..., description="Risk level: Low, Medium, or High")
    confidence: float = Field(
        ..., description="Prediction confidence score", ge=0, le=1
    )
    outbreak_threshold: float = Field(
        ..., description="Threshold for outbreak classification"
    )
    features_used: int = Field(..., description="Number of features used in prediction")
    timestamp: datetime = Field(..., description="Prediction timestamp")


# ============================================================================
# Model Schemas
# ============================================================================


class ModelStatsResponse(BaseModel):
    """Response model for model statistics"""

    status: str = Field(..., description="Model status: loaded or not_loaded")
    model_type: Optional[str] = Field(None, description="Type of ML model")
    features_count: Optional[int] = Field(None, description="Number of features")
    feature_list: Optional[List[str]] = Field(None, description="List of feature names")
    outbreak_threshold: Optional[float] = Field(None, description="Outbreak threshold")
    performance_metrics: Optional[Dict[str, float]] = Field(
        None, description="Model metrics"
    )
    data_source: Optional[str] = Field(
        None, description="Data source used for training"
    )


class ModelReloadResponse(BaseModel):
    """Response model for model reload"""

    status: str
    message: str


# ============================================================================
# Health Schemas
# ============================================================================


class HealthResponse(BaseModel):
    """Response model for health check"""

    status: str = Field(..., description="API health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    model_status: str = Field(..., description="Model loading status")
    message: Optional[str] = Field(None, description="Additional information")


class RootResponse(BaseModel):
    """Response model for root endpoint"""

    message: str
    status: str
    version: str
    model_loaded: bool
    endpoints: Dict[str, str]


# ============================================================================
# Error Schemas
# ============================================================================


class ErrorResponse(BaseModel):
    """Standard error response"""

    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Auth Schemas
# ============================================================================


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
