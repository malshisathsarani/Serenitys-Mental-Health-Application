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


class ChatRequest(BaseModel):
    """Request model for chat message"""
    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    conversation_history: Optional[List[str]] = Field(None, description="Previous messages for context")
    conversation_id: Optional[int] = Field(
        None,
        ge=1,
        description="Existing conversation id to continue; omit to start a new conversation",
    )
    voice_risk_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Optional voice-derived risk score (0.0-1.0) from audio analysis",
    )
    voice_crisis_detected: Optional[bool] = Field(
        None,
        description="Optional voice crisis flag from audio analysis",
    )
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat message"""
    response: str = Field(..., description="Chatbot's response")
    conversation_id: int = Field(..., description="Conversation this exchange belongs to")
    assistant_message_id: int = Field(
        ...,
        description="Database id of the assistant message (for feedback and multimodal metadata)",
    )
    prediction: Optional[str] = Field(None, description="Mental health prediction")
    probabilities: Dict[str, float] = Field(default_factory=dict, description="Prediction probabilities")
    crisis_detected: bool = Field(False, description="Whether crisis situation detected (fused)")
    crisis_fusion_sources: List[str] = Field(
        default_factory=list,
        description="Which signals contributed to crisis_detected (e.g. text, voice)",
    )
    fused_risk_score: Optional[float] = Field(
        None,
        description="Combined text+voice risk score (0.0-1.0) when available",
    )
    voice_risk_score: Optional[float] = Field(
        None,
        description="Voice-only risk score (0.0-1.0) when provided",
    )
    requires_professional_help: bool = Field(False, description="Whether professional help recommended")
    crisis_resources: Optional[Dict] = Field(None, description="Crisis support resources if applicable")
    status: str = Field(..., description="Status of the operation")


class VoiceAnalysisResponse(BaseModel):
    """Response model for uploaded audio risk analysis."""
    voice_risk_score: float = Field(..., ge=0.0, le=1.0)
    voice_crisis_detected: bool = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)
    method: str = Field(..., description="How audio was analyzed")
    details: Dict[str, float] = Field(default_factory=dict)
    status: str = Field(..., description="Status of operation")


class FeedbackRequest(BaseModel):
    """Request model for assistant response feedback."""
    message_id: int = Field(..., ge=1, description="Assistant message id")
    helpful: bool = Field(..., description="Whether response felt appropriate/fair")
    comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional feedback note",
    )


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    feedback_id: int
    message_id: int
    helpful: bool
    status: str


class MessageResponse(BaseModel):
    """Response model for a single message"""
    id: int
    role: str
    content: str
    timestamp: datetime
    prediction: Optional[str] = None
    probabilities: Optional[Dict[str, float]] = None
    crisis_detected: bool = False
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response model for conversation list"""
    id: int
    title: str
    started_at: datetime
    last_message_at: datetime
    message_count: int
    is_active: bool
    crisis_detected: bool
    
    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Response model for conversation with messages"""
    id: int
    title: str
    started_at: datetime
    last_message_at: datetime
    message_count: int
    is_active: bool
    crisis_detected: bool
    messages: List[MessageResponse]
    
    class Config:
        from_attributes = True


class EmergencyContactRequest(BaseModel):
    """Request model for adding emergency contact"""
    name: str = Field(..., min_length=1, max_length=255, description="Contact name or title")
    phone_number: str = Field(..., description="Phone number in E.164 format (e.g., +12025551234)")
    contact_relationship: Optional[str] = Field(None, max_length=100, description="Relationship description")
    is_hotline: Optional[bool] = Field(False, description="Whether this is a crisis hotline")
    
    @validator('phone_number')
    def validate_phone(cls, v):
        # Basic E.164 format validation (+ followed by 1-15 digits)
        import re
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone must be in E.164 format (e.g., +12025551234)')
        return v


class EmergencyContactResponse(BaseModel):
    """Response model for emergency contact"""
    id: int
    name: str
    phone_number: str
    contact_relationship: Optional[str]
    is_hotline: bool
    is_active: bool
    status: str
    
    class Config:
        from_attributes = True


class EmergencyCallResponse(BaseModel):
    """Response model for emergency call record"""
    id: int
    phone_number: str
    call_sid: Optional[str]
    status: str
    crisis_type: Optional[str]
    fused_risk_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmergencyCallListResponse(BaseModel):
    """Response model for list of emergency calls"""
    total_calls: int
    calls: List[EmergencyCallResponse]
    status: str

