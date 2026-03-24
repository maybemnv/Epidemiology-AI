"""
Data Ingestion Routes

Endpoints for ingesting outbreak, environmental, and digital signals data.
"""

from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.core import get_db
from ...database.models import User, Disease, GeographicRegion
from ..schemas import (
    OutbreakDataIngest,
    EnvironmentalDataIngest,
    DigitalSignalIngest,
    IngestionResponse,
)
from ..dependencies import get_current_active_user
from ...services.etl import ETLService

router = APIRouter(prefix="/data", tags=["Data Ingestion"])


@router.post("/outbreaks", response_model=IngestionResponse)
async def ingest_outbreak_data(
    data: List[OutbreakDataIngest],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Ingest outbreak data from external sources.

    Accepts batch data for bulk insertion. Requires authentication.
    """
    etl = ETLService(db)

    for record in data:
        disease = await db.get(Disease, record.disease_id)
        if not disease:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Disease with ID {record.disease_id} not found",
            )

        region = await db.get(GeographicRegion, record.region_id)
        if not region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Region with ID {record.region_id} not found",
            )

    raw_data = [record.model_dump() for record in data]
    result = await etl.ingest_outbreak_data(raw_data)

    return IngestionResponse(
        success=result.success,
        records_processed=result.records_processed,
        records_inserted=result.records_inserted,
        records_updated=result.records_updated,
        errors=result.errors,
    )


@router.post("/environmental", response_model=IngestionResponse)
async def ingest_environmental_data(
    data: List[EnvironmentalDataIngest],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Ingest environmental/weather data from external sources.

    Accepts batch data for bulk insertion. Requires authentication.
    """
    etl = ETLService(db)

    for record in data:
        region = await db.get(GeographicRegion, record.region_id)
        if not region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Region with ID {record.region_id} not found",
            )

    raw_data = [record.model_dump() for record in data]
    result = await etl.ingest_environmental_data(raw_data)

    return IngestionResponse(
        success=result.success,
        records_processed=result.records_processed,
        records_inserted=result.records_inserted,
        records_updated=result.records_updated,
        errors=result.errors,
    )


@router.post("/digital-signals", response_model=IngestionResponse)
async def ingest_digital_signals(
    data: List[DigitalSignalIngest],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Ingest digital surveillance signals (Google Trends, social media, etc.).

    Accepts batch data for bulk insertion. Requires authentication.
    """
    etl = ETLService(db)

    for record in data:
        region = await db.get(GeographicRegion, record.region_id)
        if not region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Region with ID {record.region_id} not found",
            )

        if record.disease_id:
            disease = await db.get(Disease, record.disease_id)
            if not disease:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Disease with ID {record.disease_id} not found",
                )

    raw_data = [record.model_dump() for record in data]
    result = await etl.ingest_digital_signals(raw_data)

    return IngestionResponse(
        success=result.success,
        records_processed=result.records_processed,
        records_inserted=result.records_inserted,
        records_updated=result.records_updated,
        errors=result.errors,
    )
