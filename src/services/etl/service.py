"""
ETL Service

Orchestrates ETL operations for all data types.
"""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from .pipeline import etl_pipeline, ETLResult
from .loader import DataLoader

logger = logging.getLogger(__name__)


class ETLService:
    """Main ETL service orchestrating validation, cleaning, and loading"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.loader = DataLoader(db)

    async def ingest_outbreak_data(self, raw_data: List[Dict[str, Any]]) -> ETLResult:
        """Ingest outbreak data through full ETL pipeline"""
        logger.info(f"Starting outbreak data ingestion: {len(raw_data)} records")

        cleaned_data, validation_result = etl_pipeline.process_outbreak_data(raw_data)

        if not validation_result.success:
            logger.warning(
                f"Outbreak data validation had {len(validation_result.errors)} errors"
            )

        inserted, updated = await self.loader.load_outbreak_data(cleaned_data)

        return ETLResult(
            success=validation_result.success,
            records_processed=validation_result.records_processed,
            records_inserted=inserted,
            records_updated=updated,
            errors=validation_result.errors,
        )

    async def ingest_environmental_data(
        self, raw_data: List[Dict[str, Any]]
    ) -> ETLResult:
        """Ingest environmental data through full ETL pipeline"""
        logger.info(f"Starting environmental data ingestion: {len(raw_data)} records")

        cleaned_data, validation_result = etl_pipeline.process_environmental_data(
            raw_data
        )

        if not validation_result.success:
            logger.warning(
                f"Environmental data validation had {len(validation_result.errors)} errors"
            )

        inserted, updated = await self.loader.load_environmental_data(cleaned_data)

        return ETLResult(
            success=validation_result.success,
            records_processed=validation_result.records_processed,
            records_inserted=inserted,
            records_updated=updated,
            errors=validation_result.errors,
        )

    async def ingest_digital_signals(self, raw_data: List[Dict[str, Any]]) -> ETLResult:
        """Ingest digital signals through full ETL pipeline"""
        logger.info(f"Starting digital signals ingestion: {len(raw_data)} records")

        cleaned_data, validation_result = etl_pipeline.process_digital_signals(raw_data)

        if not validation_result.success:
            logger.warning(
                f"Digital signals validation had {len(validation_result.errors)} errors"
            )

        inserted, updated = await self.loader.load_digital_signals(cleaned_data)

        return ETLResult(
            success=validation_result.success,
            records_processed=validation_result.records_processed,
            records_inserted=inserted,
            records_updated=updated,
            errors=validation_result.errors,
        )
