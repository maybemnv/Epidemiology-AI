"""
Database Models

SQLAlchemy models for the Epidemiology AI application.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .core import Base

# ============================================================================
# Core Tables
# ============================================================================


class User(Base):
    """User for authentication and RBAC"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[Optional[str]] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    alerts_managed: Mapped[List["Alert"]] = relationship(
        "Alert", back_populates="assignee"
    )


class Disease(Base):
    """Disease metadata (e.g. Dengue, Malaria)"""

    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)  # e.g., "Dengue"
    description: Mapped[Optional[str]] = mapped_column(String)
    vector: Mapped[Optional[str]] = mapped_column(String)  # e.g., "Aedes aegypti"

    # Relationships
    outbreaks: Mapped[List["OutbreakData"]] = relationship(
        "OutbreakData", back_populates="disease"
    )
    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction", back_populates="disease"
    )


class GeographicRegion(Base):
    """Locations monitored for outbreaks"""

    __tablename__ = "geographic_regions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)  # e.g., "San Juan"
    code: Mapped[str] = mapped_column(String, unique=True, index=True)  # e.g., "sj"
    country: Mapped[str] = mapped_column(String)  # e.g. "Puerto Rico"
    coordinates: Mapped[Optional[dict]] = mapped_column(
        JSON
    )  # {"lat": 18.46, "lon": -66.1}
    population: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    outbreaks: Mapped[List["OutbreakData"]] = relationship(
        "OutbreakData", back_populates="region"
    )
    environment_data: Mapped[List["EnvironmentalData"]] = relationship(
        "EnvironmentalData", back_populates="region"
    )
    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction", back_populates="region"
    )
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="region")


# ============================================================================
# Data Tables
# ============================================================================


class OutbreakData(Base):
    """Historical case counts (Time Series)"""

    __tablename__ = "outbreak_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    year: Mapped[int] = mapped_column(Integer)
    weekofyear: Mapped[int] = mapped_column(Integer)
    total_cases: Mapped[int] = mapped_column(Integer)

    disease_id: Mapped[int] = mapped_column(ForeignKey("diseases.id"))
    region_id: Mapped[int] = mapped_column(ForeignKey("geographic_regions.id"))

    disease: Mapped["Disease"] = relationship("Disease", back_populates="outbreaks")
    region: Mapped["GeographicRegion"] = relationship(
        "GeographicRegion", back_populates="outbreaks"
    )


class EnvironmentalData(Base):
    """Weather and environmental metrics"""

    __tablename__ = "environmental_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    weekofyear: Mapped[int] = mapped_column(Integer)

    # Weather Metrics
    temp_avg: Mapped[float] = mapped_column(Float)
    temp_min: Mapped[float] = mapped_column(Float)
    temp_max: Mapped[float] = mapped_column(Float)
    precipitation_mm: Mapped[float] = mapped_column(Float)
    humidity_percent: Mapped[float] = mapped_column(Float)
    ndvi_ne: Mapped[Optional[float]] = mapped_column(Float)  # Vegetation index
    ndvi_nw: Mapped[Optional[float]] = mapped_column(Float)
    ndvi_se: Mapped[Optional[float]] = mapped_column(Float)
    ndvi_sw: Mapped[Optional[float]] = mapped_column(Float)

    region_id: Mapped[int] = mapped_column(ForeignKey("geographic_regions.id"))
    region: Mapped["GeographicRegion"] = relationship(
        "GeographicRegion", back_populates="environment_data"
    )


class DigitalSignal(Base):
    """Digital signals data (Google Trends, social media)"""

    __tablename__ = "digital_signals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    keyword: Mapped[str] = mapped_column(String, nullable=False)
    signal_value: Mapped[float] = mapped_column(Float, nullable=False)
    region_id: Mapped[int] = mapped_column(ForeignKey("geographic_regions.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ============================================================================
# Analysis Tables
# ============================================================================


class Prediction(Base):
    """Model predictions"""

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    prediction_date: Mapped[datetime] = mapped_column(
        DateTime
    )  # Target date for prediction

    predicted_cases: Mapped[float] = mapped_column(Float)
    confidence_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String)  # Low, Medium, High
    features_used: Mapped[Optional[dict]] = mapped_column(
        JSON
    )  # Snapshot of input features

    disease_id: Mapped[int] = mapped_column(ForeignKey("diseases.id"))
    region_id: Mapped[int] = mapped_column(ForeignKey("geographic_regions.id"))
    model_version_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("model_versions.id")
    )

    disease: Mapped["Disease"] = relationship("Disease", back_populates="predictions")
    region: Mapped["GeographicRegion"] = relationship(
        "GeographicRegion", back_populates="predictions"
    )
    model_version: Mapped["ModelVersion"] = relationship(
        "ModelVersion", back_populates="predictions"
    )


class Alert(Base):
    """Generated alerts for outbreaks"""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    severity: Mapped[str] = mapped_column(String)  # Warning, Critical
    message: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(
        String, default="New"
    )  # New, Acknowledged, Resolved

    region_id: Mapped[int] = mapped_column(ForeignKey("geographic_regions.id"))
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    region: Mapped["GeographicRegion"] = relationship(
        "GeographicRegion", back_populates="alerts"
    )
    assignee: Mapped["User"] = relationship("User", back_populates="alerts_managed")


class ModelVersion(Base):
    """ML Model version tracking"""

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    version: Mapped[str] = mapped_column(String, unique=True)
    algorithm: Mapped[str] = mapped_column(String)  # XGBoost, Random Forest
    training_date: Mapped[datetime] = mapped_column(DateTime)
    metrics: Mapped[dict] = mapped_column(JSON)  # {"mae": 12.5, "r2": 0.78}
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction", back_populates="model_version"
    )
