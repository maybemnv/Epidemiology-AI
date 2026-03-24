"""
Dashboard & Analytics Routes

Endpoints for dashboard data and analytics.
"""

from datetime import datetime
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct

from ...database.core import get_db
from ...database.models import (
    Alert,
    OutbreakData,
    Prediction,
    GeographicRegion,
    Disease,
)
from ..schemas import (
    DashboardOverview,
    MapDataResponse,
    MapRegionData,
    TrendAnalysisResponse,
    TrendDataPoint,
)

router = APIRouter(tags=["Dashboard & Analytics"])

DEFAULT_LIMIT = 100
DEFAULT_PREDICTION_HORIZON = 7
DEFAULT_AGGREGATION = "weekly"


@router.get("/dashboard/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    region_id: Optional[int] = Query(None, description="Filter by region"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Get high-level dashboard metrics"""
    alert_query = select(func.count(Alert.id)).where(Alert.is_resolved.is_(False))
    outbreak_query = select(func.count(distinct(OutbreakData.region_id))).where(
        OutbreakData.case_count > 0
    )
    prediction_query = select(func.count(Prediction.id)).where(
        Prediction.risk_level.in_(["high", "critical"])
    )

    if region_id:
        alert_query = alert_query.where(Alert.region_id == region_id)
        outbreak_query = outbreak_query.where(OutbreakData.region_id == region_id)
        prediction_query = prediction_query.where(Prediction.region_id == region_id)

    total_alerts = (await db.execute(alert_query)).scalar() or 0
    active_outbreaks = (await db.execute(outbreak_query)).scalar() or 0
    at_risk_regions = (await db.execute(prediction_query)).scalar() or 0

    return DashboardOverview(
        total_alerts=total_alerts,
        active_outbreaks=active_outbreaks,
        at_risk_regions=at_risk_regions,
    )


@router.get("/dashboard/map-data", response_model=MapDataResponse)
async def get_map_data(
    disease_id: Optional[int] = Query(None, description="Filter by disease"),
    date: Optional[datetime] = Query(None, description="Filter by date"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Get geospatial risk data for map visualization"""
    query = select(
        GeographicRegion.id,
        GeographicRegion.name,
        GeographicRegion.latitude,
        GeographicRegion.longitude,
        func.coalesce(func.max(OutbreakData.case_count), 0).label("case_count"),
        func.coalesce(func.max(Prediction.risk_level), "low").label("risk_level"),
        func.coalesce(func.max(Prediction.predicted_value), 0).label(
            "prediction_score"
        ),
    ).join(OutbreakData, isouter=True)

    if disease_id:
        query = query.where(OutbreakData.disease_id == disease_id)
    if date:
        query = query.where(OutbreakData.date >= date)

    query = query.group_by(
        GeographicRegion.id,
        GeographicRegion.name,
        GeographicRegion.latitude,
        GeographicRegion.longitude,
    )

    result = await db.execute(query)
    rows = result.all()

    regions = [
        MapRegionData(
            region_id=row.id,
            region_name=row.name,
            latitude=float(row.latitude) if row.latitude else None,
            longitude=float(row.longitude) if row.longitude else None,
            risk_level=row.risk_level,
            case_count=row.case_count,
            prediction_score=(
                float(row.prediction_score) if row.prediction_score else None
            ),
        )
        for row in rows
    ]

    return MapDataResponse(
        regions=regions, disease_id=disease_id, date=date or datetime.now()
    )


@router.get("/analytics/trends", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    disease_id: int = Query(..., description="Disease ID"),
    region_id: int = Query(..., description="Region ID"),
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    aggregation_period: str = Query(
        DEFAULT_AGGREGATION, description="daily, weekly, monthly"
    ),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Get time-series trend data for analysis"""
    outbreak_query = (
        select(
            OutbreakData.date,
            func.sum(OutbreakData.case_count).label("total_cases"),
        )
        .where(
            OutbreakData.disease_id == disease_id,
            OutbreakData.region_id == region_id,
            OutbreakData.date >= start_date,
            OutbreakData.date <= end_date,
        )
        .group_by(OutbreakData.date)
        .order_by(OutbreakData.date)
    )

    prediction_query = (
        select(
            Prediction.prediction_date,
            func.avg(Prediction.predicted_value).label("avg_predicted"),
            Prediction.risk_level,
        )
        .where(
            Prediction.disease_id == disease_id,
            Prediction.region_id == region_id,
            Prediction.prediction_date >= start_date,
            Prediction.prediction_date <= end_date,
        )
        .group_by(Prediction.prediction_date, Prediction.risk_level)
        .order_by(Prediction.prediction_date)
    )

    outbreak_result = await db.execute(outbreak_query)
    outbreak_data = {row.date: row.total_cases for row in outbreak_result.all()}

    prediction_result = await db.execute(prediction_query)
    prediction_data = {
        row.prediction_date: {"predicted": row.avg_predicted, "risk": row.risk_level}
        for row in prediction_result.all()
    }

    all_dates = sorted(set(outbreak_data.keys()) | set(prediction_data.keys()))

    trend_data = []
    for dt in all_dates:
        trend_data.append(
            TrendDataPoint(
                date=dt,
                actual_cases=outbreak_data.get(dt),
                predicted_cases=prediction_data.get(dt, {}).get("predicted"),
                risk_level=prediction_data.get(dt, {}).get("risk"),
            )
        )

    return TrendAnalysisResponse(
        disease_id=disease_id,
        region_id=region_id,
        data=trend_data,
        aggregation_period=aggregation_period,
    )


@router.get("/predictions", response_model=list[dict])
async def list_predictions(
    disease_id: Optional[int] = Query(None),
    region_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    risk_level: Optional[str] = Query(None),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=1000),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Get predictions with filtering"""
    query = select(Prediction).order_by(Prediction.prediction_date.desc()).limit(limit)

    if disease_id:
        query = query.where(Prediction.disease_id == disease_id)
    if region_id:
        query = query.where(Prediction.region_id == region_id)
    if start_date:
        query = query.where(Prediction.prediction_date >= start_date)
    if end_date:
        query = query.where(Prediction.prediction_date <= end_date)
    if risk_level:
        query = query.where(Prediction.risk_level == risk_level)

    result = await db.execute(query)
    predictions = result.scalars().all()

    return [
        {
            "id": p.id,
            "disease_id": p.disease_id,
            "region_id": p.region_id,
            "prediction_date": p.prediction_date,
            "predicted_value": float(p.predicted_value) if p.predicted_value else None,
            "risk_level": p.risk_level,
            "created_at": p.created_at,
        }
        for p in predictions
    ]


@router.post("/predictions/generate")
async def generate_predictions(
    disease_id: int,
    region_id: int,
    prediction_horizon_days: int = Query(DEFAULT_PREDICTION_HORIZON, ge=1, le=30),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Trigger prediction generation for a disease-region pair"""
    disease = await db.get(Disease, disease_id)
    if not disease:
        raise HTTPException(
            status_code=400,
            detail=f"Disease with ID {disease_id} not found",
        )

    region = await db.get(GeographicRegion, region_id)
    if not region:
        raise HTTPException(
            status_code=400,
            detail=f"Region with ID {region_id} not found",
        )

    return {
        "status": "queued",
        "disease_id": disease_id,
        "region_id": region_id,
        "prediction_horizon_days": prediction_horizon_days,
        "message": "Prediction job queued (requires Celery worker)",
    }
