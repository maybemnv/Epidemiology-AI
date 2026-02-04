"""
Service Layer for Model Operations

Provides business logic for outbreak predictions and model management.
"""

from typing import Dict, Any, List, Optional
from .predictor import OutbreakPredictor


class ModelService:
    """Service for managing model predictions and operations"""

    def __init__(self, model_path: str = "../models/dengue_outbreak_predictor.pkl"):
        """
        Initialize model service

        Args:
            model_path: Path to the trained model file
        """
        self.predictor: Optional[OutbreakPredictor] = None
        self.model_path = model_path
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the predictor"""
        try:
            self.predictor = OutbreakPredictor(self.model_path)
        except Exception as e:
            print(f"⚠ Failed to initialize model: {e}")
            self.predictor = None

    def is_model_loaded(self) -> bool:
        """Check if model is loaded and ready"""
        return self.predictor is not None and self.predictor.is_loaded()

    def predict_outbreak(
        self,
        temp_avg: float,
        temp_min: float,
        temp_max: float,
        precipitation_mm: float,
        humidity_percent: float,
        weekofyear: int,
        previous_cases: List[int],
    ) -> Dict[str, Any]:
        """
        Predict outbreak risk

        Returns:
            Prediction results with risk assessment
        """
        if not self.is_model_loaded():
            raise ValueError("Model not loaded. Please train and save a model first.")

        return self.predictor.predict(
            temp_avg=temp_avg,
            temp_min=temp_min,
            temp_max=temp_max,
            precipitation_mm=precipitation_mm,
            humidity_percent=humidity_percent,
            weekofyear=weekofyear,
            previous_cases=previous_cases,
        )

    def get_model_statistics(self) -> Dict[str, Any]:
        """Get model performance statistics and metadata"""
        if not self.is_model_loaded():
            return {
                "status": "not_loaded",
                "message": (
                    "Model not loaded. Run the training notebook " "to create a model."
                ),
            }

        return {"status": "loaded", **self.predictor.get_model_info()}

    def reload_model(self) -> bool:
        """Reload the model from disk"""
        try:
            self._initialize_model()
            return self.is_model_loaded()
        except Exception as e:
            print(f"✗ Failed to reload model: {e}")
            return False
