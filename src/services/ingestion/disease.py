from typing import Any, Dict, List
from datetime import datetime
import pandas as pd


from .base import BaseIngestionService
from ...database.models import OutbreakData


class DiseaseDataIngestionService(BaseIngestionService):
    """Ingest disease outbreak data from CSV files."""

    async def fetch_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load CSV file and return as list of dicts."""
        df = pd.read_csv(file_path)
        return df.to_dict("records")

    async def transform_data(
        self, raw_data: List[Dict[str, Any]], disease_id: int, region_id: int
    ) -> List[OutbreakData]:
        """Transform CSV rows to OutbreakData models."""
        models = []

        for row in raw_data:
            try:
                year = int(row.get("year", row.get("Year", 0)))
                week = int(row.get("weekofyear", row.get("week_of_year", 0)))
                cases = int(row.get("total_cases", row.get("cases", 0)))

                date_str = row.get("week_start_date")
                if date_str:
                    date_obj = pd.to_datetime(date_str).to_pydatetime()
                else:
                    date_obj = datetime(year, 1, 1) + pd.Timedelta(weeks=week - 1)

                model = OutbreakData(
                    date=date_obj,
                    year=year,
                    weekofyear=week,
                    total_cases=cases,
                    disease_id=disease_id,
                    region_id=region_id,
                )
                models.append(model)
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to error: {e}, row: {row}")
                continue

        return models

    async def ingest(
        self, file_path: str, disease_id: int, region_id: int
    ) -> Dict[str, Any]:
        """Ingest disease data from CSV file."""
        raw_data = await self.fetch_data(file_path)
        models = await self.transform_data(raw_data, disease_id, region_id)
        count = await self.save_to_db(models)

        return {
            "status": "success",
            "records_ingested": count,
            "disease_id": disease_id,
            "region_id": region_id,
            "source_file": file_path,
            "timestamp": datetime.now(),
        }
