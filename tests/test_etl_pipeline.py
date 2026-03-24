"""
Tests for ETL Pipeline

Test validation, cleaning, and loading.
"""

import pytest
from datetime import datetime
from src.services.etl.pipeline import DataValidator, DataCleaner, ETLPipeline


class TestDataValidator:
    @pytest.fixture
    def validator(self):
        return DataValidator()

    def test_validate_outbreak_data_valid(self, validator):
        data = {
            "disease_id": 1,
            "region_id": 1,
            "date": datetime.now(),
            "case_count": 10,
        }
        is_valid, error = validator.validate_outbreak_data(data)
        assert is_valid is True
        assert error == ""

    def test_validate_outbreak_data_missing_disease(self, validator):
        data = {"region_id": 1, "date": datetime.now(), "case_count": 10}
        is_valid, error = validator.validate_outbreak_data(data)
        assert is_valid is False
        assert "Missing disease_id" in error

    def test_validate_outbreak_data_negative_cases(self, validator):
        data = {
            "disease_id": 1,
            "region_id": 1,
            "date": datetime.now(),
            "case_count": -5,
        }
        is_valid, error = validator.validate_outbreak_data(data)
        assert is_valid is False
        assert "negative" in error

    def test_validate_environmental_data_valid(self, validator):
        data = {
            "region_id": 1,
            "date": datetime.now(),
            "temperature_avg": 25.5,
            "rainfall_mm": 10.0,
            "humidity_avg": 70.0,
        }
        is_valid, error = validator.validate_environmental_data(data)
        assert is_valid is True

    def test_validate_environmental_data_invalid_temp(self, validator):
        data = {
            "region_id": 1,
            "date": datetime.now(),
            "temperature_avg": 100,
            "rainfall_mm": 10.0,
            "humidity_avg": 70.0,
        }
        is_valid, error = validator.validate_environmental_data(data)
        assert is_valid is False
        assert "Invalid temperature" in error

    def test_validate_digital_signal_valid(self, validator):
        data = {
            "region_id": 1,
            "date": datetime.now(),
            "signal_type": "search_trend",
            "signal_source": "google_trends",
            "signal_value": 75.0,
        }
        is_valid, error = validator.validate_digital_signal(data)
        assert is_valid is True


class TestDataCleaner:
    @pytest.fixture
    def cleaner(self):
        return DataCleaner()

    def test_clean_outbreak_data(self, cleaner):
        data = {
            "disease_id": 1,
            "region_id": 1,
            "date": "2024-01-01T00:00:00Z",
            "case_count": 10,
            "hospitalization_count": 2,
            "is_preliminary": True,
        }
        cleaned = cleaner.clean_outbreak_data(data)
        assert cleaned["case_count"] == 10
        assert cleaned["hospitalization_count"] == 2
        assert cleaned["is_preliminary"] is True
        assert isinstance(cleaned["date"], datetime)

    def test_clean_outbreak_data_negative_values(self, cleaner):
        data = {
            "disease_id": 1,
            "region_id": 1,
            "date": datetime.now(),
            "case_count": -5,
            "hospitalization_count": -2,
        }
        cleaned = cleaner.clean_outbreak_data(data)
        assert cleaned["case_count"] == 0
        assert cleaned["hospitalization_count"] == 0

    def test_clean_environmental_data(self, cleaner):
        data = {
            "region_id": 1,
            "date": "2024-01-01",
            "temperature_avg": 25.555,
            "temperature_min": 20.111,
            "temperature_max": 30.999,
            "rainfall_mm": 10.5,
            "humidity_avg": 75.5,
        }
        cleaned = cleaner.clean_environmental_data(data)
        assert cleaned["temperature_avg"] == 25.56
        assert cleaned["temperature_min"] == 20.11
        assert cleaned["temperature_max"] == 31.0
        assert cleaned["humidity_avg"] == 75.5

    def test_clean_environmental_data_humidity_bounds(self, cleaner):
        data = {
            "region_id": 1,
            "date": datetime.now(),
            "temperature_avg": 25.0,
            "rainfall_mm": 10.0,
            "humidity_avg": 150.0,
        }
        cleaned = cleaner.clean_environmental_data(data)
        assert cleaned["humidity_avg"] == 100.0

    def test_detect_outliers(self, cleaner):
        values = [10, 12, 11, 13, 100, 12, 11]
        outliers = cleaner.detect_outliers(values)
        assert 4 in outliers

    def test_detect_outliers_none(self, cleaner):
        values = [10, 12, 11, 13, 12, 11, 10]
        outliers = cleaner.detect_outliers(values)
        assert len(outliers) == 0


class TestETLPipeline:
    @pytest.fixture
    def pipeline(self):
        return ETLPipeline(DataValidator(), DataCleaner())

    def test_process_outbreak_data(self, pipeline):
        raw_data = [
            {
                "disease_id": 1,
                "region_id": 1,
                "date": "2024-01-01",
                "case_count": 10,
            },
            {
                "disease_id": 1,
                "region_id": 1,
                "date": "2024-01-02",
                "case_count": -5,
            },
        ]
        cleaned, result = pipeline.process_outbreak_data(raw_data)
        assert result.records_processed == 2
        assert len(cleaned) == 1
        assert len(result.errors) == 1

    def test_process_environmental_data(self, pipeline):
        raw_data = [
            {
                "region_id": 1,
                "date": "2024-01-01",
                "temperature_avg": 25.0,
                "temperature_min": 20.0,
                "temperature_max": 30.0,
                "rainfall_mm": 10.0,
                "humidity_avg": 70.0,
            }
        ]
        cleaned, result = pipeline.process_environmental_data(raw_data)
        assert result.success is True
        assert len(cleaned) == 1

    def test_process_digital_signals(self, pipeline):
        raw_data = [
            {
                "region_id": 1,
                "date": "2024-01-01",
                "signal_type": "search_trend",
                "signal_source": "google_trends",
                "signal_value": 75.0,
            }
        ]
        cleaned, result = pipeline.process_digital_signals(raw_data)
        assert result.success is True
        assert len(cleaned) == 1
