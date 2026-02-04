"""
Model Predictor Module

Handles ML model loading and prediction logic with proper feature engineering.
"""

import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OutbreakPredictor:
    """Dengue outbreak prediction model wrapper"""

    def __init__(self, model_path: str):
        """
        Initialize predictor with trained model

        Args:
            model_path: Path to pickled model file
        """
        self.model_path = model_path
        self.model = None
        self.feature_columns: List[str] = []
        self.outbreak_threshold: float = 25.0
        self.metrics: Dict[str, float] = {}
        self.data_source: str = "Unknown"
        self._loaded = False

        self.load_model()

    def load_model(self) -> bool:
        """Load the trained ML model from disk"""
        try:
            model_file = Path(self.model_path)
            if not model_file.exists():
                logger.warning(f"Model file not found: {self.model_path}")
                return False

            with open(self.model_path, "rb") as f:
                model_data = pickle.load(f)

            self.model = model_data["model"]
            self.feature_columns = model_data["feature_columns"]
            self.outbreak_threshold = model_data.get("outbreak_threshold", 25.0)
            self.metrics = model_data.get("metrics", {})
            self.data_source = model_data.get("data_source", "Unknown")
            self._loaded = True

            return True

        except FileNotFoundError:
            logger.warning(f"Model file not found: {self.model_path}")
            return False
        except Exception as e:
            logger.error(
                f"Error loading model from {self.model_path}: {e}", exc_info=True
            )
            return False

    def is_loaded(self) -> bool:
        """Check if model is successfully loaded"""
        return self._loaded and self.model is not None

    def create_features(
        self,
        temp_avg: float,
        temp_min: float,
        temp_max: float,
        precipitation_mm: float,
        humidity_percent: float,
        weekofyear: int,
        previous_cases: List[int],
    ) -> Dict[str, float]:
        """Create features matching the training pipeline"""

        # Pad previous_cases to 4 elements
        cases = list(previous_cases)
        while len(cases) < 4:
            cases.insert(0, 0)
        cases = cases[-4:]

        features = {
            # Base weather features
            "temp_avg": temp_avg,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "precipitation_mm": precipitation_mm,
            "humidity_percent": humidity_percent,
            "weekofyear": weekofyear,
            # Lag features
            "cases_lag_1": float(cases[3]),
            "cases_lag_2": float(cases[2]),
            "cases_lag_3": float(cases[1]),
            "cases_lag_4": float(cases[0]),
            # Simplified 'rolling' features for weather (current week's value)
            # NOTE: These are NOT true rolling averages. This is a temporary compromise
            # for consistency with the training notebook due to stateless API design.
            # True rolling averages would require historical context at inference time,
            # a feature for future improvement.
            "current_temp_avg_for_roll_2w": temp_avg,
            "current_temp_avg_for_roll_4w": temp_avg,
            "current_precip_for_roll_2w": precipitation_mm,
            "current_precip_for_roll_4w": precipitation_mm,
            "current_humidity_for_roll_2w": humidity_percent,
            "current_humidity_for_roll_4w": humidity_percent,
            # Seasonal encoding
            "week_sin": np.sin(2 * np.pi * weekofyear / 52),
            "week_cos": np.cos(2 * np.pi * weekofyear / 52),
        }

        return features

    def predict(
        self,
        temp_avg: float,
        temp_min: float,
        temp_max: float,
        precipitation_mm: float,
        humidity_percent: float,
        weekofyear: int,
        previous_cases: List[int],
    ) -> Dict[str, Any]:
        """Make prediction using the loaded model"""

        if not self.is_loaded():
            raise ValueError("Model not loaded")

        # Create features
        features = self.create_features(
            temp_avg,
            temp_min,
            temp_max,
            precipitation_mm,
            humidity_percent,
            weekofyear,
            previous_cases,
        )

        # Build DataFrame
        df = pd.DataFrame([features])

        # Add missing features with zeros
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0.0

        # Select features in correct order
        df = df[self.feature_columns]

        # Predict
        predicted_cases = float(self.model.predict(df)[0])

        return {
            "predicted_cases": predicted_cases,
            "risk_level": self._assess_risk(predicted_cases),
            "confidence": self._calculate_confidence(predicted_cases),
            "threshold": self.outbreak_threshold,
            "features_used": len(self.feature_columns),
        }

    def _assess_risk(self, predicted_cases: float) -> str:
        """Determine risk level"""
        if predicted_cases < self.outbreak_threshold * 0.5:
            return "Low"
        elif predicted_cases < self.outbreak_threshold:
            return "Medium"
        return "High"

    def _calculate_confidence(self, predicted_cases: float) -> float:
        """Calculate confidence score"""
        distance = abs(predicted_cases - self.outbreak_threshold)
        normalized = min(distance / self.outbreak_threshold, 1.0)
        return round(0.70 + (normalized * 0.25), 2)

    def get_model_info(self) -> Dict[str, Any]:
        """Get model metadata"""
        if not self.is_loaded():
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "model_type": "XGBoost",
            "features_count": len(self.feature_columns),
            "feature_list": self.feature_columns,
            "outbreak_threshold": self.outbreak_threshold,
            "performance_metrics": self.metrics,
            "data_source": self.data_source,
        }
