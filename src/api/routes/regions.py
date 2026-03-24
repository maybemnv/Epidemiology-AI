"""
Region Management Routes

Endpoints for managing geographic regions.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ...database.core import get_db
from ...database.models import User, GeographicRegion, OutbreakData, Prediction
from ..schemas import RegionCreate, RegionUpdate, Region, RegionListResponse
from ..dependencies import get_current_active_superuser

router = APIRouter(prefix="/regions", tags=["Regions"])

DEFAULT_LIMIT = 100
DEFAULT_OFFSET = 0


@router.get("", response_model=RegionListResponse)
async def list_regions(
    region_type: Optional[str] = Query(None, description="Filter by region type"),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=1000),
    offset: int = Query(DEFAULT_OFFSET, ge=0),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """List all geographic regions with optional filtering"""
    query = select(GeographicRegion).order_by(GeographicRegion.name)

    if region_type:
        query = query.where(GeographicRegion.region_type == region_type)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    regions = result.scalars().all()

    count_query = select(func.count(GeographicRegion.id))
    if region_type:
        count_query = count_query.where(GeographicRegion.region_type == region_type)
    total = (await db.execute(count_query)).scalar()

    return RegionListResponse(
        data=[Region.model_validate(r) for r in regions],
        pagination={"total": total, "limit": limit, "offset": offset},
    )


@router.get("/{region_id}", response_model=Region)
async def get_region(
    region_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get specific region details"""
    region = await db.get(GeographicRegion, region_id)
    if not region:
        raise HTTPException(
            status_code=404,
            detail=f"Region with ID {region_id} not found",
        )
    return region


@router.post("", response_model=Region, status_code=201)
async def create_region(
    region_in: RegionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """Create new region (admin only)"""
    if region_in.parent_region_id:
        parent = await db.get(GeographicRegion, region_in.parent_region_id)
        if not parent:
            raise HTTPException(
                status_code=400,
                detail=f"Parent region with ID {region_in.parent_region_id} not found",
            )

    region = GeographicRegion(**region_in.model_dump())
    db.add(region)
    await db.commit()
    await db.refresh(region)
    return region


@router.put("/{region_id}", response_model=Region)
async def update_region(
    region_id: int,
    region_in: RegionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """Update region (admin only)"""
    region = await db.get(GeographicRegion, region_id)
    if not region:
        raise HTTPException(
            status_code=404,
            detail=f"Region with ID {region_id} not found",
        )

    update_data = region_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(region, field, value)

    db.add(region)
    await db.commit()
    await db.refresh(region)
    return region


@router.delete("/{region_id}", status_code=204)
async def delete_region(
    region_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """Delete region (admin only)"""
    region = await db.get(GeographicRegion, region_id)
    if not region:
        raise HTTPException(
            status_code=404,
            detail=f"Region with ID {region_id} not found",
        )

    await db.delete(region)
    await db.commit()


@router.get("/{region_id}/stats")
async def get_region_stats(
    region_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get aggregate statistics for a region"""
    region = await db.get(GeographicRegion, region_id)
    if not region:
        raise HTTPException(
            status_code=404,
            detail=f"Region with ID {region_id} not found",
        )

    outbreak_count = await db.execute(
        select(func.count(OutbreakData.id)).where(OutbreakData.region_id == region_id)
    )
    total_outbreaks = outbreak_count.scalar()

    prediction_count = await db.execute(
        select(func.count(Prediction.id)).where(Prediction.region_id == region_id)
    )
    total_predictions = prediction_count.scalar()

    latest_outbreak = await db.execute(
        select(OutbreakData)
        .where(OutbreakData.region_id == region_id)
        .order_by(OutbreakData.date.desc())
        .limit(1)
    )
    latest = latest_outbreak.scalars().first()

    return {
        "region_id": region_id,
        "region_name": region.name,
        "region_type": region.region_type,
        "population": region.population,
        "total_outbreak_records": total_outbreaks,
        "total_predictions": total_predictions,
        "latest_data_date": latest.date if latest else None,
        "latest_case_count": latest.case_count if latest else None,
    }
