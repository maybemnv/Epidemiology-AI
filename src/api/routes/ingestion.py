from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from pydantic import BaseModel
from datetime import datetime
import tempfile
import os

from ...database.core import get_db
from ...services.ingestion import (
    WeatherIngestionService,
    DiseaseDataIngestionService,
    DigitalSignalsIngestionService,
)

router = APIRouter()


class WeatherIngestRequest(BaseModel):
    region_id: int
    start_date: str
    end_date: str


class TrendsIngestRequest(BaseModel):
    keywords: List[str]
    region: str
    region_id: int
    timeframe: str = "today 3-m"


class IngestResponse(BaseModel):
    status: str
    records_ingested: int
    message: str
    timestamp: datetime


@router.post("/weather", response_model=IngestResponse)
async def ingest_weather(
    request: WeatherIngestRequest, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Ingest weather data from NOAA API."""
    try:
        service = WeatherIngestionService(db)
        result = await service.ingest(
            region_id=request.region_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        return IngestResponse(
            status=result["status"],
            records_ingested=result["records_ingested"],
            message=f"Ingested weather data for region {request.region_id}",
            timestamp=result["timestamp"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disease", response_model=IngestResponse)
async def ingest_disease_csv(
    disease_id: int,
    region_id: int,
    file: UploadFile = File(...),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Ingest disease outbreak data from CSV file."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        service = DiseaseDataIngestionService(db)
        result = await service.ingest(
            file_path=tmp_path, disease_id=disease_id, region_id=region_id
        )

        os.unlink(tmp_path)

        return IngestResponse(
            status=result["status"],
            records_ingested=result["records_ingested"],
            message=f"Ingested disease data from {file.filename}",
            timestamp=result["timestamp"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends", response_model=IngestResponse)
async def ingest_trends(
    request: TrendsIngestRequest, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Ingest digital signals from Google Trends."""
    try:
        service = DigitalSignalsIngestionService(db)
        result = await service.ingest(
            keywords=request.keywords,
            region=request.region,
            region_id=request.region_id,
            timeframe=request.timeframe,
        )

        return IngestResponse(
            status=result["status"],
            records_ingested=result["records_ingested"],
            message=f"Ingested trends for keywords: {', '.join(request.keywords)}",
            timestamp=result["timestamp"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
