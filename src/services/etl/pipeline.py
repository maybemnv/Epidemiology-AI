"""
ETL Pipeline

Core ETL pipeline for data validation, cleaning, and loading.
"""

from datetime import datetime
from typing import List, Dict, Any, TypeVar, Generic
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ETLResult(BaseModel):
    """Result of ETL operation"""

    success: bool
    records_processed: int
    records_inserted: int = 0
    records_updated: int = 0
    errors: List[str] = []


class DataValidator:
    """Validates incoming data against schemas"""

    @staticmethod
    def validate_outbreak_data(data: Dict[str, Any]) -> tuple[bool, str]:
        if not data.get("disease_id"):
            return False, "Missing disease_id"
        if not data.get("region_id"):
            return False, "Missing region_id"
        if not data.get("date"):
            return False, "Missing date"
        if data.get("case_count", 0) < 0:
            return False, "case_count cannot be negative"
        if data.get("hospitalization_count", 0) < 0:
            return False, "hospitalization_count cannot be negative"
        return True, ""

    @staticmethod
    def validate_environmental_data(data: Dict[str, Any]) -> tuple[bool, str]:
        if not data.get("region_id"):
            return False, "Missing region_id"
        if not data.get("date"):
            return False, "Missing date"
        temp = data.get("temperature_avg", 0)
        if temp < -50 or temp > 60:
            return False, f"Invalid temperature_avg: {temp}"
        rainfall = data.get("rainfall_mm", 0)
        if rainfall < 0:
            return False, f"Invalid rainfall_mm: {rainfall}"
        humidity = data.get("humidity_avg", 0)
        if humidity < 0 or humidity > 100:
            return False, f"Invalid humidity_avg: {humidity}"
        return True, ""

    @staticmethod
    def validate_digital_signal(data: Dict[str, Any]) -> tuple[bool, str]:
        if not data.get("region_id"):
            return False, "Missing region_id"
        if not data.get("date"):
            return False, "Missing date"
        if not data.get("signal_type"):
            return False, "Missing signal_type"
        if not data.get("signal_source"):
            return False, "Missing signal_source"
        if data.get("signal_value", 0) < 0:
            return False, "signal_value cannot be negative"
        return True, ""


class DataCleaner:
    """Cleans and normalizes data"""

    @staticmethod
    def clean_outbreak_data(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = data.copy()
        cleaned["case_count"] = max(0, int(data.get("case_count", 0)))
        cleaned["hospitalization_count"] = max(
            0, int(data.get("hospitalization_count", 0))
        )
        cleaned["death_count"] = max(0, int(data.get("death_count", 0)))
        cleaned["recovered_count"] = max(0, int(data.get("recovered_count", 0)))
        cleaned["is_preliminary"] = bool(data.get("is_preliminary", False))
        if "date" in cleaned and isinstance(cleaned["date"], str):
            cleaned["date"] = datetime.fromisoformat(
                cleaned["date"].replace("Z", "+00:00")
            )
        return cleaned

    @staticmethod
    def clean_environmental_data(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = data.copy()
        cleaned["temperature_avg"] = round(float(data.get("temperature_avg", 0)), 2)
        cleaned["temperature_min"] = round(float(data.get("temperature_min", 0)), 2)
        cleaned["temperature_max"] = round(float(data.get("temperature_max", 0)), 2)
        cleaned["rainfall_mm"] = round(float(data.get("rainfall_mm", 0)), 2)
        cleaned["humidity_avg"] = round(
            min(100, max(0, float(data.get("humidity_avg", 0)))), 2
        )
        if data.get("wind_speed_avg"):
            cleaned["wind_speed_avg"] = round(max(0, float(data["wind_speed_avg"])), 2)
        if data.get("vector_index"):
            cleaned["vector_index"] = round(max(0, float(data["vector_index"])), 2)
        if "date" in cleaned and isinstance(cleaned["date"], str):
            cleaned["date"] = datetime.fromisoformat(
                cleaned["date"].replace("Z", "+00:00")
            )
        return cleaned

    @staticmethod
    def clean_digital_signal(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = data.copy()
        cleaned["signal_value"] = round(max(0, float(data.get("signal_value", 0))), 4)
        if data.get("signal_volume"):
            cleaned["signal_volume"] = max(0, int(data["signal_volume"]))
        cleaned["is_anomaly"] = bool(data.get("is_anomaly", False))
        if "date" in cleaned and isinstance(cleaned["date"], str):
            cleaned["date"] = datetime.fromisoformat(
                cleaned["date"].replace("Z", "+00:00")
            )
        return cleaned

    @staticmethod
    def handle_missing_values(
        records: List[Dict[str, Any]], strategy: str = "ffill"
    ) -> List[Dict[str, Any]]:
        if not records:
            return records

        if strategy == "ffill":
            last_valid = {}
            for record in records:
                for key, value in record.items():
                    if value is not None:
                        last_valid[key] = value
                    elif key in last_valid:
                        record[key] = last_valid[key]
        elif strategy == "bfill":
            next_valid = {}
            for record in reversed(records):
                for key, value in record.items():
                    if value is not None:
                        next_valid[key] = value
                    elif key in next_valid:
                        record[key] = next_valid[key]

        return records

    @staticmethod
    def detect_outliers(values: List[float], threshold: float = 3.0) -> List[int]:
        if len(values) < 3:
            return []

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance**0.5

        if std_dev == 0:
            return []

        outliers = []
        for i, value in enumerate(values):
            z_score = abs(value - mean) / std_dev
            if z_score > threshold:
                outliers.append(i)

        return outliers


class ETLPipeline(Generic[T]):
    """Main ETL pipeline orchestrator"""

    def __init__(self, validator: DataValidator, cleaner: DataCleaner):
        self.validator = validator
        self.cleaner = cleaner

    def process_outbreak_data(
        self, raw_data: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], ETLResult]:
        errors = []
        cleaned_records = []

        for i, record in enumerate(raw_data):
            is_valid, error_msg = self.validator.validate_outbreak_data(record)
            if not is_valid:
                errors.append(f"Record {i}: {error_msg}")
                continue

            try:
                cleaned = self.cleaner.clean_outbreak_data(record)
                cleaned_records.append(cleaned)
            except Exception as e:
                errors.append(f"Record {i}: Cleaning error - {str(e)}")

        result = ETLResult(
            success=len(errors) == 0,
            records_processed=len(raw_data),
            errors=errors,
        )

        return cleaned_records, result

    def process_environmental_data(
        self, raw_data: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], ETLResult]:
        errors = []
        cleaned_records = []

        for i, record in enumerate(raw_data):
            is_valid, error_msg = self.validator.validate_environmental_data(record)
            if not is_valid:
                errors.append(f"Record {i}: {error_msg}")
                continue

            try:
                cleaned = self.cleaner.clean_environmental_data(record)
                cleaned_records.append(cleaned)
            except Exception as e:
                errors.append(f"Record {i}: Cleaning error - {str(e)}")

        result = ETLResult(
            success=len(errors) == 0,
            records_processed=len(raw_data),
            errors=errors,
        )

        return cleaned_records, result

    def process_digital_signals(
        self, raw_data: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], ETLResult]:
        errors = []
        cleaned_records = []

        for i, record in enumerate(raw_data):
            is_valid, error_msg = self.validator.validate_digital_signal(record)
            if not is_valid:
                errors.append(f"Record {i}: {error_msg}")
                continue

            try:
                cleaned = self.cleaner.clean_digital_signal(record)
                cleaned_records.append(cleaned)
            except Exception as e:
                errors.append(f"Record {i}: Cleaning error - {str(e)}")

        result = ETLResult(
            success=len(errors) == 0,
            records_processed=len(raw_data),
            errors=errors,
        )

        return cleaned_records, result


# Global pipeline instance
_validator = DataValidator()
_cleaner = DataCleaner()
etl_pipeline = ETLPipeline(_validator, _cleaner)
