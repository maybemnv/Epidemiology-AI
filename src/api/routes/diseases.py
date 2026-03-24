"""
Disease Management Routes

Endpoints for managing disease metadata.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ...database.core import get_db
from ...database.models import User, Disease
from ..schemas import DiseaseCreate, DiseaseUpdate, Disease, DiseaseListResponse
from ..dependencies import get_current_active_superuser

router = APIRouter(prefix="/diseases", tags=["Diseases"])

DEFAULT_LIMIT = 100
DEFAULT_OFFSET = 0


@router.get("", response_model=DiseaseListResponse)
async def list_diseases(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=1000),
    offset: int = Query(DEFAULT_OFFSET, ge=0),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """List all diseases with pagination"""
    query = select(Disease).order_by(Disease.name).offset(offset).limit(limit)
    result = await db.execute(query)
    diseases = result.scalars().all()

    count_query = select(func.count(Disease.id))
    total = (await db.execute(count_query)).scalar()

    return DiseaseListResponse(
        data=[Disease.model_validate(d) for d in diseases],
        pagination={"total": total, "limit": limit, "offset": offset},
    )


@router.get("/{disease_id}", response_model=Disease)
async def get_disease(
    disease_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get specific disease details"""
    disease = await db.get(Disease, disease_id)
    if not disease:
        raise HTTPException(
            status_code=404,
            detail=f"Disease with ID {disease_id} not found",
        )
    return disease


@router.post("", response_model=Disease, status_code=201)
async def create_disease(
    disease_in: DiseaseCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """Create new disease (admin only)"""
    existing = await db.execute(select(Disease).where(Disease.name == disease_in.name))
    if existing.scalars().first():
        raise HTTPException(
            status_code=400,
            detail=f"Disease with name '{disease_in.name}' already exists",
        )

    disease = Disease(**disease_in.model_dump())
    db.add(disease)
    await db.commit()
    await db.refresh(disease)
    return disease


@router.put("/{disease_id}", response_model=Disease)
async def update_disease(
    disease_id: int,
    disease_in: DiseaseUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """Update disease (admin only)"""
    disease = await db.get(Disease, disease_id)
    if not disease:
        raise HTTPException(
            status_code=404,
            detail=f"Disease with ID {disease_id} not found",
        )

    update_data = disease_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(disease, field, value)

    db.add(disease)
    await db.commit()
    await db.refresh(disease)
    return disease


@router.delete("/{disease_id}", status_code=204)
async def delete_disease(
    disease_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """Delete disease (admin only)"""
    disease = await db.get(Disease, disease_id)
    if not disease:
        raise HTTPException(
            status_code=404,
            detail=f"Disease with ID {disease_id} not found",
        )

    await db.delete(disease)
    await db.commit()
