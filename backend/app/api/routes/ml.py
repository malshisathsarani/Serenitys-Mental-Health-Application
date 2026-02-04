"""
ML API Routes
Endpoints for mental health text analysis
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.schemas import TextInput, PredictionResponse, ModelInfoResponse
from app.services.ml_service import get_ml_service, MLService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.post("/predict", response_model=PredictionResponse)
async def predict_mental_health(
    input_data: TextInput,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Analyze text and predict mental health status
    
    - **text**: Text content to analyze (10-5000 characters)
    
    Returns prediction and confidence probabilities for each class
    """
    result = ml_service.predict(input_data.text)
    
    if result['status'] == 'error':
        raise HTTPException(status_code=500, detail=result.get('message', 'Prediction failed'))
    
    return result


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info(ml_service: MLService = Depends(get_ml_service)):
    """Get information about the loaded ML model"""
    return ml_service.get_model_info()
