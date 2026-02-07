from typing import Any, Dict, List
from datetime import datetime
import requests
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseIngestionService
from ...database.models import EnvironmentalData
from ...core.config import get_settings

settings = get_settings()


class WeatherIngestionService(BaseIngestionService):
    """Ingest weather data from NOAA API."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.api_key = getattr(settings, "NOAA_API_KEY", None)
        self.base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2"

    async def fetch_data(
        self, region_id: int, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """Fetch weather data from NOAA API."""
        if not self.api_key:
            raise ValueError("NOAA_API_KEY not configured")

        headers = {"token": self.api_key}
        params = {
            "datasetid": "GHCND",
            "startdate": start_date,
            "enddate": end_date,
            "limit": 1000,
        }

        response = requests.get(
            f"{self.base_url}/data", headers=headers, params=params, timeout=30
        )
        response.raise_for_status()

        return response.json().get("results", [])

    async def transform_data(
        self, raw_data: List[Dict[str, Any]], region_id: int
    ) -> List[EnvironmentalData]:
        """Transform NOAA data to EnvironmentalData models."""
        models = []

        data_by_date = {}
        for record in raw_data:
            date = record.get("date")
            datatype = record.get("datatype")
            value = record.get("value")

            if date not in data_by_date:
                data_by_date[date] = {}

            if datatype == "TMAX":
                data_by_date[date]["temp_max"] = value / 10  # Convert to Celsius
            elif datatype == "TMIN":
                data_by_date[date]["temp_min"] = value / 10
            elif datatype == "TAVG":
                data_by_date[date]["temp_avg"] = value / 10
            elif datatype == "PRCP":
                data_by_date[date]["precipitation_mm"] = value / 10

        for date_str, values in data_by_date.items():
            date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            if all(k in values for k in ["temp_max", "temp_min", "precipitation_mm"]):
                temp_avg = values.get(
                    "temp_avg", (values["temp_max"] + values["temp_min"]) / 2
                )

                model = EnvironmentalData(
                    date=date_obj,
                    weekofyear=date_obj.isocalendar()[1],
                    temp_avg=temp_avg,
                    temp_min=values["temp_min"],
                    temp_max=values["temp_max"],
                    precipitation_mm=values["precipitation_mm"],
                    humidity_percent=75.0,  # Default value
                    region_id=region_id,
                )
                models.append(model)

        return models

    async def ingest(
        self, region_id: int, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """Ingest weather data for a specific region and date range."""
        raw_data = await self.fetch_data(region_id, start_date, end_date)
        models = await self.transform_data(raw_data, region_id)
        count = await self.save_to_db(models)

        return {
            "status": "success",
            "records_ingested": count,
            "region_id": region_id,
            "date_range": f"{start_date} to {end_date}",
            "timestamp": datetime.now(),
        }
