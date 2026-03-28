"""
Pydantic Models/Schemas
Request and response models for API endpoints
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Dict, Optional
from datetime import datetime


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class UserRegister(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 chars)")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscore, and hyphen')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: 'UserResponse' = Field(..., description="User information")


class UserResponse(BaseModel):
    """User information response"""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    full_name: Optional[str] = Field(None, description="Full name")
    is_active: bool = Field(..., description="Account active")
    is_verified: bool = Field(..., description="Email verified")
    created_at: datetime = Field(..., description="Account creation date")
    last_login_at: Optional[datetime] = Field(None, description="Last login")
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User profile update"""
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None)
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change request"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 chars)")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# ============================================================================
# ML & CHAT SCHEMAS (existing)
# ============================================================================

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
