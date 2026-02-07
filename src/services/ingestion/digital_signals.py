from typing import Any, Dict, List
from datetime import datetime
from pytrends.request import TrendReq
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseIngestionService
from ...database.models import DigitalSignal


class DigitalSignalsIngestionService(BaseIngestionService):
    """Ingest digital signals data from Google Trends."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.pytrends = TrendReq(hl="en-US", tz=360)

    async def fetch_data(
        self, keywords: List[str], region: str, timeframe: str = "today 3-m"
    ) -> List[Dict[str, Any]]:
        """Fetch Google Trends data for keywords."""
        self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=region)
        interest_over_time = self.pytrends.interest_over_time()

        if interest_over_time.empty:
            return []

        results = []
        for date, row in interest_over_time.iterrows():
            for keyword in keywords:
                if keyword in row:
                    results.append(
                        {
                            "date": date,
                            "keyword": keyword,
                            "interest_score": int(row[keyword]),
                        }
                    )

        return results

    async def transform_data(
        self, raw_data: List[Dict[str, Any]], region_id: int
    ) -> List[DigitalSignal]:
        """Transform trends data to DigitalSignal models."""
        models = []

        for record in raw_data:
            model = DigitalSignal(
                date=record["date"],
                source="google_trends",
                keyword=record["keyword"],
                signal_value=record["interest_score"],
                region_id=region_id,
            )
            models.append(model)

        return models

    async def ingest(
        self,
        keywords: List[str],
        region: str,
        region_id: int,
        timeframe: str = "today 3-m",
    ) -> Dict[str, Any]:
        """Ingest Google Trends data."""
        raw_data = await self.fetch_data(keywords, region, timeframe)
        models = await self.transform_data(raw_data, region_id)
        count = await self.save_to_db(models)

        return {
            "status": "success",
            "records_ingested": count,
            "keywords": keywords,
            "region": region,
            "region_id": region_id,
            "timeframe": timeframe,
            "timestamp": datetime.now(),
        }
