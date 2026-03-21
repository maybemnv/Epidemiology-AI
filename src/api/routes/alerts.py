"""
Alert Management Routes

Endpoints for managing outbreak alerts.
"""

from datetime import datetime
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ...database.core import get_db
from ...database.models import Alert, GeographicRegion, User
from .. import schemas
from ..dependencies import get_current_active_user, get_current_active_superuser

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# Query parameter defaults
STATUS_FILTER_QUERY = Query(None, alias="status", description="Filter by status")
SEVERITY_QUERY = Query(None, description="Filter by severity")
LIMIT_QUERY = Query(100, ge=1, le=1000, description="Maximum number of alerts")
SKIP_QUERY = Query(0, ge=0, description="Number of alerts to skip")


@router.get("", response_model=List[schemas.Alert])
async def get_all_alerts(
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: str = STATUS_FILTER_QUERY,
    severity: str = SEVERITY_QUERY,
    limit: int = LIMIT_QUERY,
    skip: int = SKIP_QUERY,
):
    """
    Get all alerts with optional filtering.

    **Filters:**
    - **status**: Filter by alert status (New, Acknowledged, Resolved)
    - **severity**: Filter by severity level (Warning, Critical)

    **Pagination:**
    - **limit**: Maximum number of results (default: 100, max: 1000)
    - **skip**: Number of results to skip (default: 0)
    """
    query = select(Alert)

    if status_filter:
        query = query.where(Alert.status == status_filter)
    if severity:
        query = query.where(Alert.severity == severity)

    query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    return alerts


@router.get("/{alert_id}", response_model=schemas.Alert)
async def get_alert(
    alert_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get details of a specific alert by ID.
    """
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalars().first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found",
        )

    return alert


@router.post("", response_model=schemas.Alert, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_in: schemas.AlertCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """
    Create a new alert. **Requires superuser privileges.**

    **Parameters:**
    - **severity**: Alert severity (Warning or Critical)
    - **message**: Alert message describing the situation
    - **region_id**: ID of the affected region
    - **assigned_to_id**: Optional user ID to assign the alert to
    """
    # Verify region exists
    region_result = await db.execute(
        select(GeographicRegion).where(GeographicRegion.id == alert_in.region_id)
    )
    region = region_result.scalars().first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Region with ID {alert_in.region_id} not found",
        )

    # Verify assigned user exists if provided
    if alert_in.assigned_to_id:
        user_result = await db.execute(
            select(User).where(User.id == alert_in.assigned_to_id)
        )
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID {alert_in.assigned_to_id} not found",
            )

    # Create alert
    alert = Alert(
        severity=alert_in.severity,
        message=alert_in.message,
        region_id=alert_in.region_id,
        assigned_to_id=alert_in.assigned_to_id,
        status="New",
    )

    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    return alert


@router.put("/{alert_id}", response_model=schemas.Alert)
async def update_alert(
    alert_id: int,
    alert_in: schemas.AlertUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """
    Update an alert. **Requires superuser privileges.**

    Any field can be updated. Only provided fields will be updated.
    """
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalars().first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found",
        )

    # Update fields
    update_data = alert_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)

    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    return alert


@router.post("/{alert_id}/acknowledge", response_model=schemas.Alert)
async def acknowledge_alert(
    alert_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Acknowledge an alert. Marks the alert as "Acknowledged" and assigns
    it to current user.

    Any authenticated user can acknowledge alerts.
    """
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalars().first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found",
        )

    alert.status = "Acknowledged"
    alert.assigned_to_id = current_user.id

    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    return alert


@router.post("/{alert_id}/resolve", response_model=schemas.Alert)
async def resolve_alert(
    alert_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """
    Resolve an alert. Marks the alert as "Resolved". **Requires superuser privileges.**
    """
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalars().first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found",
        )

    alert.status = "Resolved"

    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """
    Delete an alert. **Requires superuser privileges.**
    """
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalars().first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found",
        )

    await db.delete(alert)
    await db.commit()

    return None


@router.get("/stats/summary")
async def get_alerts_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get summary statistics for alerts.

    Returns counts by status and severity for dashboard display.
    """
    # Count by status
    status_query = select(Alert.status, func.count(Alert.id)).group_by(Alert.status)
    status_result = await db.execute(status_query)
    by_status = {row[0]: row[1] for row in status_result.all()}

    # Count by severity
    severity_query = select(Alert.severity, func.count(Alert.id)).group_by(
        Alert.severity
    )
    severity_result = await db.execute(severity_query)
    by_severity = {row[0]: row[1] for row in severity_result.all()}

    # Total alerts
    total_query = select(func.count(Alert.id))
    total = (await db.execute(total_query)).scalar()

    # New alerts (require action)
    new_query = select(func.count(Alert.id)).where(Alert.status == "New")
    new_count = (await db.execute(new_query)).scalar()

    return {
        "total": total,
        "by_status": by_status,
        "by_severity": by_severity,
        "new_alerts": new_count,
        "timestamp": datetime.now(),
    }
