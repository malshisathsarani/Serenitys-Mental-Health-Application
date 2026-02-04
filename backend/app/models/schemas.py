"""
Pydantic Models/Schemas
Request and response models for API endpoints
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional


class TextInput(BaseModel):
    """Request model for text analysis"""
    text: str = Field(..., min_length=10, max_length=5000, description="Text to analyze")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Text must be at least 10 characters')
        return v.strip()


class PredictionResponse(BaseModel):
    """Response model for prediction"""
    prediction: Optional[str] = Field(None, description="Predicted mental health status")
    probabilities: Dict[str, float] = Field(default_factory=dict, description="Prediction probabilities")
    status: str = Field(..., description="Status of the operation")
    message: Optional[str] = Field(None, description="Error message if status is error")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment")


class ModelInfoResponse(BaseModel):
    """Response model for model information"""
    classes: list = Field(..., description="List of classification classes")
    model_type: str = Field(..., description="Type of ML model")
    vocabulary_size: int = Field(..., description="Size of vocabulary")
    model_path: str = Field(..., description="Path to model file")
