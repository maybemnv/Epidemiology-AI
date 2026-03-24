"""
Weather Data Client

NOAA API client for weather data ingestion.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
import logging

from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WeatherDataClient:
    """Client for NOAA weather API"""

    def __init__(self):
        self.api_key = settings.NOAA_API_KEY
        self.base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2"

    async def fetch_data(
        self,
        lat: float,
        lon: float,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, Any]]:
        """Fetch weather data from NOAA API"""
        if not self.api_key:
            logger.warning("NOAA_API_KEY not configured, returning mock data")
            return self._generate_mock_data(start_date, end_date)

        try:
            headers = {"token": self.api_key}
            params = {
                "datasetid": "GHCND",
                "startdate": start_date.strftime("%Y-%m-%d"),
                "enddate": end_date.strftime("%Y-%m-%d"),
                "limit": 1000,
            }

            response = requests.get(
                f"{self.base_url}/data", headers=headers, params=params, timeout=30
            )
            response.raise_for_status()
            data = response.json().get("results", [])

            return self._parse_noaa_data(data)

        except requests.RequestException as e:
            logger.error(f"NOAA API request failed: {e}")
            return self._generate_mock_data(start_date, end_date)

    def _parse_noaa_data(self, raw_data: List[Dict]) -> List[Dict[str, Any]]:
        """Parse NOAA API response to standard format"""
        data_by_date = {}

        for record in raw_data:
            date_str = record.get("date", "")[:10]
            datatype = record.get("datatype", "")
            value = record.get("value", 0)

            if date_str not in data_by_date:
                data_by_date[date_str] = {}

            if datatype == "TMAX":
                data_by_date[date_str]["temp_max"] = value / 10
            elif datatype == "TMIN":
                data_by_date[date_str]["temp_min"] = value / 10
            elif datatype == "TAVG":
                data_by_date[date_str]["temp_avg"] = value / 10
            elif datatype == "PRCP":
                data_by_date[date_str]["precipitation_mm"] = value / 10
            elif datatype == "AWND":
                data_by_date[date_str]["wind_speed_avg"] = value / 10
            elif datatype == "RHAV":
                data_by_date[date_str]["humidity_avg"] = value

        result = []
        for date_str, values in data_by_date.items():
            if len(values) >= 3:
                date_obj = datetime.fromisoformat(date_str)
                temp_avg = values.get(
                    "temp_avg",
                    (values.get("temp_max", 25) + values.get("temp_min", 20)) / 2,
                )
                result.append(
                    {
                        "date": date_obj,
                        "temperature_avg": temp_avg,
                        "temperature_min": values.get("temp_min", 20.0),
                        "temperature_max": values.get("temp_max", 30.0),
                        "rainfall_mm": values.get("precipitation_mm", 0.0),
                        "humidity_avg": values.get("humidity_avg", 70.0),
                        "wind_speed_avg": values.get("wind_speed_avg"),
                        "data_source": "noaa",
                    }
                )

        return result

    def _generate_mock_data(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate mock weather data for testing"""
        import random

        result = []
        current = start_date
        while current <= end_date:
            result.append(
                {
                    "date": current,
                    "temperature_avg": round(random.uniform(20, 35), 2),
                    "temperature_min": round(random.uniform(15, 25), 2),
                    "temperature_max": round(random.uniform(25, 40), 2),
                    "rainfall_mm": round(random.uniform(0, 50), 2),
                    "humidity_avg": round(random.uniform(50, 90), 2),
                    "wind_speed_avg": round(random.uniform(0, 20), 2),
                    "data_source": "mock",
                }
            )
            current += timedelta(days=1)

        return result
