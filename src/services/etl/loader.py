"""
ETL Data Loader

Handles bulk loading of cleaned data into the database.
"""

from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..database.models import (
    OutbreakData,
    EnvironmentalData,
    DigitalSignal,
)

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads cleaned data into database with upsert logic"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def load_outbreak_data(
        self, records: List[Dict[str, Any]]
    ) -> tuple[int, int]:
        """
        Load outbreak data with upsert logic.
        Returns (inserted_count, updated_count)
        """
        inserted = 0
        updated = 0

        for record in records:
            try:
                existing = await self.db.execute(
                    select(OutbreakData).where(
                        OutbreakData.disease_id == record["disease_id"],
                        OutbreakData.region_id == record["region_id"],
                        OutbreakData.date == record["date"],
                    )
                )
                existing_record = existing.scalars().first()

                if existing_record:
                    for key, value in record.items():
                        if key not in ["disease_id", "region_id", "date"]:
                            setattr(existing_record, key, value)
                    existing_record.updated_at = datetime.now()
                    updated += 1
                else:
                    new_record = OutbreakData(**record)
                    self.db.add(new_record)
                    inserted += 1

            except SQLAlchemyError as e:
                logger.error(f"Error loading outbreak data: {e}")
                continue

        await self.db.commit()
        return inserted, updated

    async def load_environmental_data(
        self, records: List[Dict[str, Any]]
    ) -> tuple[int, int]:
        """
        Load environmental data with upsert logic.
        Returns (inserted_count, updated_count)
        """
        inserted = 0
        updated = 0

        for record in records:
            try:
                existing = await self.db.execute(
                    select(EnvironmentalData).where(
                        EnvironmentalData.region_id == record["region_id"],
                        EnvironmentalData.date == record["date"],
                    )
                )
                existing_record = existing.scalars().first()

                if existing_record:
                    for key, value in record.items():
                        if key not in ["region_id", "date"]:
                            setattr(existing_record, key, value)
                    existing_record.updated_at = datetime.now()
                    updated += 1
                else:
                    new_record = EnvironmentalData(**record)
                    self.db.add(new_record)
                    inserted += 1

            except SQLAlchemyError as e:
                logger.error(f"Error loading environmental data: {e}")
                continue

        await self.db.commit()
        return inserted, updated

    async def load_digital_signals(
        self, records: List[Dict[str, Any]]
    ) -> tuple[int, int]:
        """
        Load digital signals with upsert logic.
        Returns (inserted_count, updated_count)
        """
        inserted = 0
        updated = 0

        for record in records:
            try:
                existing = await self.db.execute(
                    select(DigitalSignal).where(
                        DigitalSignal.region_id == record["region_id"],
                        DigitalSignal.date == record["date"],
                        DigitalSignal.signal_type == record["signal_type"],
                        DigitalSignal.signal_source == record["signal_source"],
                    )
                )
                existing_record = existing.scalars().first()

                if existing_record:
                    for key, value in record.items():
                        if key not in [
                            "region_id",
                            "date",
                            "signal_type",
                            "signal_source",
                        ]:
                            setattr(existing_record, key, value)
                    existing_record.updated_at = datetime.now()
                    updated += 1
                else:
                    new_record = DigitalSignal(**record)
                    self.db.add(new_record)
                    inserted += 1

            except SQLAlchemyError as e:
                logger.error(f"Error loading digital signal: {e}")
                continue

        await self.db.commit()
        return inserted, updated
