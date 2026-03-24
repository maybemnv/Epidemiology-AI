"""
Digital Signals Client

Google Trends client for digital signals ingestion.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from pytrends.request import TrendReq

logger = logging.getLogger(__name__)


class DigitalSignalsClient:
    """Client for Google Trends API via pytrends"""

    def __init__(self):
        self.pytrends = TrendReq(hl="en-US", tz=360)

    async def fetch_data(
        self,
        region_id: int,
        keywords: Optional[List[str]] = None,
        days: int = 30,
        geo: str = "US",
    ) -> List[Dict[str, Any]]:
        """Fetch Google Trends data"""
        if keywords is None:
            keywords = ["dengue fever", "dengue symptoms", "fever treatment"]

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            timeframe = (
                f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}"
            )

            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
            interest_over_time = self.pytrends.interest_over_time()

            if interest_over_time.empty:
                logger.warning(f"No trends data for keywords: {keywords}")
                return []

            return self._parse_trends_data(interest_over_time, keywords, region_id)

        except Exception as e:
            logger.error(f"Google Trends request failed: {e}")
            return self._generate_mock_data(keywords, region_id, days)

    def _parse_trends_data(
        self, df, keywords: List[str], region_id: int
    ) -> List[Dict[str, Any]]:
        """Parse pytrends DataFrame to standard format"""
        result = []

        for date, row in df.iterrows():
            for keyword in keywords:
                if keyword in row and row[keyword] is not None:
                    result.append(
                        {
                            "date": date.to_pydatetime(),
                            "region_id": region_id,
                            "signal_type": "search_trend",
                            "signal_source": "google_trends",
                            "signal_value": float(row[keyword]),
                            "signal_volume": None,
                            "is_anomaly": False,
                        }
                    )

        return result

    def _generate_mock_data(
        self, keywords: List[str], region_id: int, days: int
    ) -> List[Dict[str, Any]]:
        """Generate mock trends data for testing"""
        import random

        result = []
        current = datetime.now() - timedelta(days=days)
        end_date = datetime.now()

        while current <= end_date:
            for _ in keywords:
                result.append(
                    {
                        "date": current,
                        "region_id": region_id,
                        "signal_type": "search_trend",
                        "signal_source": "google_trends_mock",
                        "signal_value": float(random.randint(10, 90)),
                        "signal_volume": random.randint(100, 10000),
                        "is_anomaly": False,
                    }
                )
            current += timedelta(days=1)

        return result
