"""
API Schemas

Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum

# =============================================================================
# Enums
# =============================================================================


class UserRole(str, Enum):
    ADMIN = "admin"
    HEALTH_OFFICIAL = "health_official"
    ANALYST = "analyst"
    RESEARCHER = "researcher"


class RegionType(str, Enum):
    COUNTRY = "country"
    STATE = "state"
    DISTRICT = "district"
    CITY = "city"
    PINCODE = "pincode"


class SignalType(str, Enum):
    SEARCH_TREND = "search_trend"
    SOCIAL_MEDIA = "social_media"
    PHARMACY_SALES = "pharmacy_sales"
    MOBILITY = "mobility"


class PredictionType(str, Enum):
    RISK_SCORE = "risk_score"
    CASE_COUNT = "case_count"
    OUTBREAK_PROBABILITY = "outbreak_probability"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    OUTBREAK_PREDICTION = "outbreak_prediction"
    RISK_ELEVATION = "risk_elevation"
    ANOMALY_DETECTED = "anomaly_detected"
    TREND_CHANGE = "trend_change"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class AccessLevel(str, Enum):
    READ = "read"
    READ_WRITE = "read_write"
    ADMIN = "admin"


# =============================================================================
# Authentication Schemas
# =============================================================================


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None
    role: UserRole = UserRole.ANALYST
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =============================================================================
# Disease Schemas
# =============================================================================


class DiseaseBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    transmission_type: Optional[str] = Field(None, max_length=100)
    seasonal_pattern: Optional[str] = Field(None, max_length=255)


class DiseaseCreate(DiseaseBase):
    pass


class DiseaseUpdate(BaseModel):
    description: Optional[str] = None
    transmission_type: Optional[str] = None
    seasonal_pattern: Optional[str] = None


class Disease(DiseaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class DiseaseListResponse(BaseModel):
    data: List[Disease]
    pagination: Dict[str, int]


# =============================================================================
# Geographic Region Schemas
# =============================================================================


class RegionBase(BaseModel):
    name: str = Field(..., max_length=255)
    region_type: RegionType = RegionType.CITY
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    population: Optional[int] = Field(None, ge=0)
    area_sqkm: Optional[float] = Field(None, ge=0)
    parent_region_id: Optional[int] = None


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    name: Optional[str] = None
    population: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Region(RegionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RegionListResponse(BaseModel):
    data: List[Region]
    pagination: Dict[str, int]


# =============================================================================
# Outbreak Data Schemas (ETL)
# =============================================================================


class OutbreakDataBase(BaseModel):
    disease_id: int
    region_id: int
    date: datetime
    case_count: int = Field(..., ge=0)
    hospitalization_count: Optional[int] = Field(0, ge=0)
    death_count: Optional[int] = Field(0, ge=0)
    recovered_count: Optional[int] = Field(0, ge=0)
    data_source: Optional[str] = Field(None, max_length=100)
    is_preliminary: bool = False


class OutbreakDataCreate(OutbreakDataBase):
    pass


class OutbreakData(OutbreakDataBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class OutbreakDataIngest(BaseModel):
    """Schema for bulk ingestion of outbreak data"""

    disease_id: int
    region_id: int
    date: datetime
    case_count: int = Field(..., ge=0)
    hospitalization_count: int = 0
    death_count: int = 0
    recovered_count: int = 0
    data_source: Optional[str] = None
    is_preliminary: bool = False


# =============================================================================
# Environmental Data Schemas (ETL)
# =============================================================================


class EnvironmentalDataBase(BaseModel):
    region_id: int
    date: datetime
    temperature_avg: float = Field(..., ge=-50, le=60)
    temperature_min: float = Field(..., ge=-50, le=60)
    temperature_max: float = Field(..., ge=-50, le=60)
    rainfall_mm: float = Field(..., ge=0)
    humidity_avg: float = Field(..., ge=0, le=100)
    wind_speed_avg: Optional[float] = Field(None, ge=0)
    vector_index: Optional[float] = Field(None, ge=0)
    data_source: Optional[str] = Field(None, max_length=100)


class EnvironmentalDataCreate(EnvironmentalDataBase):
    pass


class EnvironmentalData(EnvironmentalDataBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class EnvironmentalDataIngest(BaseModel):
    """Schema for bulk ingestion of environmental data"""

    region_id: int
    date: datetime
    temperature_avg: float
    temperature_min: float
    temperature_max: float
    rainfall_mm: float
    humidity_avg: float
    wind_speed_avg: Optional[float] = None
    vector_index: Optional[float] = None
    data_source: Optional[str] = None


# =============================================================================
# Digital Signal Schemas (ETL)
# =============================================================================


class DigitalSignalBase(BaseModel):
    region_id: int
    disease_id: Optional[int] = None
    date: datetime
    signal_type: SignalType
    signal_source: str = Field(..., max_length=100)
    signal_value: float = Field(..., ge=0)
    signal_volume: Optional[int] = Field(None, ge=0)
    is_anomaly: bool = False


class DigitalSignalCreate(DigitalSignalBase):
    pass


class DigitalSignal(DigitalSignalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class DigitalSignalIngest(BaseModel):
    """Schema for bulk ingestion of digital signals"""

    region_id: int
    disease_id: Optional[int] = None
    date: datetime
    signal_type: SignalType
    signal_source: str
    signal_value: float
    signal_volume: Optional[int] = None


# =============================================================================
# Prediction Schemas
# =============================================================================


class PredictionBase(BaseModel):
    disease_id: int
    region_id: int
    prediction_date: datetime
    actual_date: Optional[datetime] = None
    prediction_type: PredictionType = PredictionType.CASE_COUNT
    predicted_value: float
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None
    model_version: Optional[str] = None
    features_used: Optional[Dict[str, Any]] = None
    risk_level: RiskLevel = RiskLevel.LOW
    is_alert_triggered: bool = False


class PredictionCreate(PredictionBase):
    pass


class Prediction(PredictionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PredictionResponse(BaseModel):
    predicted_cases: float
    risk_level: str
    confidence: float
    outbreak_threshold: float
    features_used: Dict[str, Any]
    timestamp: datetime


class PredictionRequest(BaseModel):
    temp_avg: float
    temp_min: float
    temp_max: float
    precipitation_mm: float
    humidity_percent: float
    weekofyear: int = Field(..., ge=1, le=53)
    previous_cases: List[int] = Field(..., min_length=1, max_length=4)


# =============================================================================
# Alert Schemas
# =============================================================================


class AlertBase(BaseModel):
    prediction_id: Optional[int] = None
    region_id: int
    disease_id: int
    assigned_to_id: Optional[int] = None
    alert_type: AlertType = AlertType.OUTBREAK_PREDICTION
    severity: AlertSeverity = AlertSeverity.WARNING
    title: str = Field(..., max_length=500)
    description: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    severity: Optional[AlertSeverity] = None
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to_id: Optional[int] = None


class Alert(AlertBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_acknowledged: bool
    acknowledged_by_id: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    is_resolved: bool
    resolved_by_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class AlertAcknowledge(BaseModel):
    notes: Optional[str] = None


class AlertResolve(BaseModel):
    resolution_notes: Optional[str] = None
    action_taken: Optional[str] = None


# =============================================================================
# Model Version Schemas
# =============================================================================


class ModelVersionBase(BaseModel):
    model_name: str = Field(..., max_length=255)
    model_version: str = Field(..., max_length=50)
    model_type: str = Field(..., max_length=100)
    training_date: datetime
    training_data_range_start: Optional[datetime] = None
    training_data_range_end: Optional[datetime] = None
    model_metrics: Optional[Dict[str, Any]] = None
    model_artifact_path: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class ModelVersionCreate(ModelVersionBase):
    pass


class ModelVersion(ModelVersionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ModelStatsResponse(BaseModel):
    status: str
    model_type: Optional[str] = None
    feature_count: Optional[int] = None
    feature_list: Optional[List[str]] = None
    outbreak_threshold: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    message: Optional[str] = None


class ModelReloadResponse(BaseModel):
    status: str
    message: str


# =============================================================================
# Dashboard & Analytics Schemas
# =============================================================================


class DashboardOverview(BaseModel):
    total_alerts: int
    active_outbreaks: int
    at_risk_regions: int
    prediction_accuracy: Optional[float] = None
    data_completeness: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class MapRegionData(BaseModel):
    region_id: int
    region_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    risk_level: str
    case_count: int
    prediction_score: Optional[float] = None


class MapDataResponse(BaseModel):
    regions: List[MapRegionData]
    disease_id: Optional[int] = None
    date: datetime


class TrendDataPoint(BaseModel):
    date: datetime
    actual_cases: Optional[int] = None
    predicted_cases: Optional[float] = None
    risk_level: Optional[str] = None


class TrendAnalysisResponse(BaseModel):
    disease_id: int
    region_id: int
    data: List[TrendDataPoint]
    aggregation_period: str


# =============================================================================
# ETL & Ingestion Schemas
# =============================================================================


class IngestionResponse(BaseModel):
    success: bool
    records_processed: int
    records_inserted: int
    records_updated: int
    errors: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.now)


class ETLJobStatus(BaseModel):
    job_id: str
    status: str  # pending, running, completed, failed
    records_processed: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


# =============================================================================
# Health Check Schemas
# =============================================================================


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)


class RootResponse(BaseModel):
    message: str
    docs_url: str
    version: str


class SystemStatusResponse(BaseModel):
    status: str
    services: Dict[str, str]
    data_latency: Optional[str] = None
    prediction_queue_size: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)
