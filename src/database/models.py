from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .core import Base

# =============================================================================
# Core Tables
# =============================================================================


class User(Base):
    """User for authentication and RBAC"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    organization: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(
        String(50), default="analyst"
    )  # admin, health_official, analyst, researcher
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    alerts_managed: Mapped[List["Alert"]] = relationship(
        "Alert", foreign_keys="Alert.assigned_to_id", back_populates="assignee"
    )
    region_access: Mapped[List["UserRegionAccess"]] = relationship(
        "UserRegionAccess", back_populates="user"
    )


class Disease(Base):
    """Disease metadata (e.g. Dengue, Malaria)"""

    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text)
    transmission_type: Mapped[Optional[str]] = mapped_column(
        String(100)
    )  # vector-borne, airborne, waterborne
    seasonal_pattern: Mapped[Optional[str]] = mapped_column(
        String(255)
    )  # monsoon, winter, year-round
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    outbreaks: Mapped[List["OutbreakData"]] = relationship(
        "OutbreakData", back_populates="disease"
    )
    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction", back_populates="disease"
    )
    digital_signals: Mapped[List["DigitalSignal"]] = relationship(
        "DigitalSignal", back_populates="disease"
    )
    symptoms: Mapped[List["DiseaseSymptom"]] = relationship(
        "DiseaseSymptom", back_populates="disease"
    )


class GeographicRegion(Base):
    """Locations monitored for outbreaks"""

    __tablename__ = "geographic_regions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    region_type: Mapped[str] = mapped_column(
        String(50), default="city"
    )  # country, state, district, city, pincode
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8))
    population: Mapped[Optional[int]] = mapped_column(Integer)
    area_sqkm: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    parent_region_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("geographic_regions.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

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
    digital_signals: Mapped[List["DigitalSignal"]] = relationship(
        "DigitalSignal", back_populates="region"
    )
    user_access: Mapped[List["UserRegionAccess"]] = relationship(
        "UserRegionAccess", back_populates="region"
    )


# =============================================================================
# Data Tables
# =============================================================================


class OutbreakData(Base):
    """Historical case counts (Time Series)"""

    __tablename__ = "outbreak_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    disease_id: Mapped[int] = mapped_column(ForeignKey("diseases.id"), nullable=False)
    region_id: Mapped[int] = mapped_column(
        ForeignKey("geographic_regions.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    case_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hospitalization_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    death_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    recovered_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    data_source: Mapped[Optional[str]] = mapped_column(String(100))
    is_preliminary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    disease: Mapped["Disease"] = relationship("Disease", back_populates="outbreaks")
    region: Mapped["GeographicRegion"] = relationship(
        "GeographicRegion", back_populates="outbreaks"
    )


class EnvironmentalData(Base):
    """Weather and environmental metrics"""

    __tablename__ = "environmental_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    region_id: Mapped[int] = mapped_column(
        ForeignKey("geographic_regions.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    temperature_avg: Mapped[float] = mapped_column(Numeric(5, 2))
    temperature_min: Mapped[float] = mapped_column(Numeric(5, 2))
    temperature_max: Mapped[float] = mapped_column(Numeric(5, 2))
    rainfall_mm: Mapped[float] = mapped_column(Numeric(7, 2))
    humidity_avg: Mapped[float] = mapped_column(Numeric(5, 2))
    wind_speed_avg: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    vector_index: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    data_source: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    region: Mapped["GeographicRegion"] = relationship(
        "GeographicRegion", back_populates="environment_data"
    )


class DigitalSignal(Base):
    """Digital signals data (Google Trends, social media)"""

    __tablename__ = "digital_signals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    region_id: Mapped[int] = mapped_column(
        ForeignKey("geographic_regions.id"), nullable=False
    )
    disease_id: Mapped[Optional[int]] = mapped_column(ForeignKey("diseases.id"))
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    signal_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # search_trend, social_media, pharmacy_sales, mobility
    signal_source: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_value: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    signal_volume: Mapped[Optional[int]] = mapped_column(Integer)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    region: Mapped["GeographicRegion"] = relationship(
        "GeographicRegion", back_populates="digital_signals"
    )
    disease: Mapped[Optional["Disease"]] = relationship(
        "Disease", back_populates="digital_signals"
    )


# =============================================================================
# Analysis Tables
# =============================================================================


class Prediction(Base):
    """Model predictions"""

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    disease_id: Mapped[int] = mapped_column(ForeignKey("diseases.id"), nullable=False)
    region_id: Mapped[int] = mapped_column(
        ForeignKey("geographic_regions.id"), nullable=False
    )
    prediction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    actual_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    prediction_type: Mapped[str] = mapped_column(
        String(50), default="case_count"
    )  # risk_score, case_count, outbreak_probability
    predicted_value: Mapped[float] = mapped_column(Numeric(10, 4))
    confidence_interval_lower: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    confidence_interval_upper: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    model_version: Mapped[Optional[str]] = mapped_column(String(50))
    features_used: Mapped[Optional[dict]] = mapped_column(JSON)
    risk_level: Mapped[str] = mapped_column(
        String(20), default="low"
    )  # low, medium, high, critical
    is_alert_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    disease: Mapped["Disease"] = relationship("Disease", back_populates="predictions")
    region: Mapped["GeographicRegion"] = relationship(
        "GeographicRegion", back_populates="predictions"
    )
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="prediction")


class Alert(Base):
    """Generated alerts for outbreaks"""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    prediction_id: Mapped[Optional[int]] = mapped_column(ForeignKey("predictions.id"))
    region_id: Mapped[int] = mapped_column(
        ForeignKey("geographic_regions.id"), nullable=False
    )
    disease_id: Mapped[int] = mapped_column(ForeignKey("diseases.id"), nullable=False)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    alert_type: Mapped[str] = mapped_column(
        String(50), default="outbreak_prediction"
    )  # outbreak_prediction, risk_elevation, anomaly_detected, trend_change
    severity: Mapped[str] = mapped_column(String(20), default="warning")
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    prediction: Mapped[Optional["Prediction"]] = relationship(
        "Prediction", back_populates="alerts"
    )
    region: Mapped["GeographicRegion"] = relationship(
        "GeographicRegion", back_populates="alerts"
    )
    disease: Mapped["Disease"] = relationship("Disease")
    assignee: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[assigned_to_id], back_populates="alerts_managed"
    )
    acknowledged_by: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[acknowledged_by_id]
    )
    resolved_by: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[resolved_by_id]
    )


class ModelVersion(Base):
    """ML Model version tracking"""

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_type: Mapped[str] = mapped_column(String(100))
    training_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    training_data_range_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    training_data_range_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    model_metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    model_artifact_path: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# =============================================================================
# Relationship Tables
# =============================================================================


class UserRegionAccess(Base):
    """User access permissions to regions"""

    __tablename__ = "user_region_access"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    region_id: Mapped[int] = mapped_column(
        ForeignKey("geographic_regions.id"), nullable=False
    )
    access_level: Mapped[str] = mapped_column(
        String(20), default="read"
    )  # read, read_write, admin
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (UniqueConstraint("user_id", "region_id", name="uq_user_region"),)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="region_access")
    region: Mapped["GeographicRegion"] = relationship(
        "GeographicRegion", back_populates="user_access"
    )


class DiseaseSymptom(Base):
    """Symptoms associated with diseases"""

    __tablename__ = "disease_symptoms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    disease_id: Mapped[int] = mapped_column(ForeignKey("diseases.id"), nullable=False)
    symptom_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    disease: Mapped["Disease"] = relationship("Disease", back_populates="symptoms")
