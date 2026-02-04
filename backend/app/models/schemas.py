"""
Pydantic Models/Schemas
Request and response models for API endpoints
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List


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


class ChatRequest(BaseModel):
    """Request model for chat message"""
    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    conversation_history: Optional[List[str]] = Field(None, description="Previous messages for context")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat message"""
    response: str = Field(..., description="Chatbot's response")
    prediction: Optional[str] = Field(None, description="Mental health prediction")
    probabilities: Dict[str, float] = Field(default_factory=dict, description="Prediction probabilities")
    crisis_detected: bool = Field(False, description="Whether crisis situation detected")
    requires_professional_help: bool = Field(False, description="Whether professional help recommended")
    crisis_resources: Optional[Dict] = Field(None, description="Crisis support resources if applicable")
    status: str = Field(..., description="Status of the operation")
