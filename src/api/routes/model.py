from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..schemas import ModelStatsResponse, ModelReloadResponse
from ..dependencies import get_model_service
from ...models.service import ModelService

router = APIRouter(prefix="/model", tags=["Model"])

# Define common dependency outside functions to avoid B008 warning
MODEL_SERVICE_DEPENDENCY = Depends(get_model_service)  # noqa: B008


@router.get("/stats", response_model=ModelStatsResponse)
async def get_model_stats(
    service: ModelService = MODEL_SERVICE_DEPENDENCY,
):
    """
    Get model performance statistics and metadata.

    **Returns:**
    - Model type (e.g., XGBoost)
    - Number of features
    - Feature list
    - Outbreak threshold
    - Performance metrics (MAE, RMSE, R²)
    - Data source used for training
    """
    stats = service.get_model_statistics()
    return ModelStatsResponse(**stats)


@router.post("/reload", response_model=ModelReloadResponse)
async def reload_model(
    service: ModelService = MODEL_SERVICE_DEPENDENCY,
):
    """
    Reload the model from disk.

    Use this after retraining the model in the notebook to load
    the updated version without restarting the server.
    """
    try:
        success = service.reload_model()

        if success:
            return ModelReloadResponse(
                status="success", message="Model reloaded successfully"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to reload model. Check if model file exists.",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")


@router.get("/features", response_model=List[str])
async def get_model_features(
    service: ModelService = MODEL_SERVICE_DEPENDENCY,
):
    """
    Get the list of features used by the model.

    Useful for understanding what data the model expects.
    """
    if not service.is_model_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")

    stats = service.get_model_statistics()
    features = stats.get("feature_list", [])
    return features
