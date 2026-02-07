from abc import ABC, abstractmethod
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


class BaseIngestionService(ABC):
    """Base class for all data ingestion services."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    @abstractmethod
    async def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch data from external source."""
        pass

    @abstractmethod
    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Any]:
        """Transform raw data into database models."""
        pass

    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data before transformation."""
        if not data:
            return False
        return True

    async def save_to_db(self, models: List[Any]) -> int:
        """Bulk insert models to database."""
        if not models:
            return 0

        self.db.add_all(models)
        await self.db.commit()
        return len(models)

    async def ingest(self, **kwargs) -> Dict[str, Any]:
        """Main ingestion flow."""
        raw_data = await self.fetch_data(**kwargs)
        models = await self.transform_data(raw_data)
        count = await self.save_to_db(models)

        return {
            "status": "success",
            "records_ingested": count,
            "timestamp": datetime.now(),
        }
