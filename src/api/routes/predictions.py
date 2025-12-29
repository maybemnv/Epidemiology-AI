"""
Prediction Routes

Endpoints for making outbreak predictions.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from ..schemas import PredictionRequest, PredictionResponse
from ..dependencies import get_model_service
from ...models.service import ModelService

router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.post("", response_model=PredictionResponse)
async def predict_outbreak(
    request: PredictionRequest,
    service: ModelService = Depends(get_model_service)
):
    """
    Predict dengue outbreak risk based on weather and historical data.
    
    **Parameters:**
    - **temp_avg**: Average temperature in Celsius
    - **temp_min**: Minimum temperature in Celsius
    - **temp_max**: Maximum temperature in Celsius
    - **precipitation_mm**: Precipitation amount in mm
    - **humidity_percent**: Relative humidity percentage
    - **weekofyear**: Week number (1-53)
    - **previous_cases**: List of case counts from previous weeks (1-4 weeks)
    
    **Returns:**
    - Predicted case count
    - Risk level (Low/Medium/High)
    - Confidence score
    - Outbreak threshold
    """
    if not service.is_model_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train and save a model first by running the notebook."
        )
    
    try:
        prediction = service.predict_outbreak(
            temp_avg=request.temp_avg,
            temp_min=request.temp_min,
            temp_max=request.temp_max,
            precipitation_mm=request.precipitation_mm,
            humidity_percent=request.humidity_percent,
            weekofyear=request.weekofyear,
            previous_cases=request.previous_cases
        )
        
        return PredictionResponse(
            predicted_cases=prediction['predicted_cases'],
            risk_level=prediction['risk_level'],
            confidence=prediction['confidence'],
            outbreak_threshold=prediction['threshold'],
            features_used=prediction['features_used'],
            timestamp=datetime.now()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
