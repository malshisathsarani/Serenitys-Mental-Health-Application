"""
Mental Health Risk API - Main Application
Production-ready FastAPI application with proper configuration and logging
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import joblib
import json
import re

from config import settings
from logging_config import setup_logging, get_logger

# =============================================================================
# Setup logging
# =============================================================================
setup_logging()
logger = get_logger(__name__)

# =============================================================================
# App initialization
# =============================================================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

logger.info("Application starting", extra={
    "app_name": settings.APP_NAME,
    "version": settings.APP_VERSION,
    "environment": settings.ENV
})

# =============================================================================
# Model loading
# =============================================================================
def load_model_and_labels():
    """Load ML model and labels from configured paths"""
    try:
        # Check for model file
        if not settings.MODEL_PATH.exists():
            error_msg = (
                f"Model file not found at {settings.MODEL_PATH}. "
                f"Please ensure the model file exists in {settings.MODEL_DIR}"
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Loading model from: {settings.MODEL_PATH}")
        model_data = joblib.load(settings.MODEL_PATH)
        
        # Handle both formats: dict with model/vectorizer or just the model
        if isinstance(model_data, dict):
            model = model_data.get("model")
            vectorizer = model_data.get("vectorizer")
            logger.info("Loaded model and vectorizer from combined file")
        else:
            model = model_data
            vectorizer = None
            logger.info("Loaded model only")

        # Load labels if available
        labels = None
        if settings.LABELS_PATH.exists():
            with open(settings.LABELS_PATH, 'r', encoding='utf-8') as f:
                labels = json.load(f)
            logger.info(f"Loaded labels from: {settings.LABELS_PATH}")
            logger.debug(f"Labels: {labels}")
        else:
            logger.warning("labels.json not found. Will use model.classes_ if available.")

        logger.info("Model loading completed successfully")
        return model, vectorizer, labels
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}", exc_info=True)
        raise

# Load model at startup
try:
    model, vectorizer, labels = load_model_and_labels()
except Exception as e:
    logger.critical(f"Failed to initialize application: {str(e)}")
    # In production, you might want to exit here
    if settings.is_production():
        raise

# =============================================================================
# Safety rules (simple critical-risk flags)
# =============================================================================
INTENT_PATTERNS = [
    r"\b(i (will|am going to|gonna))\b",
    r"\b(kill myself|end my life|suicide)\b",
    r"\b(i want to die|i don't want to live)\b",
    r"\b(can't go on|no reason to live)\b",
]

TIME_PATTERNS = [
    r"\b(today|tonight|now|right now|this evening)\b",
]

PLAN_PATTERNS = [
    r"\b(i have a plan|planned it|figured out how)\b",
]

MEANS_PATTERNS = [
    r"\b(pills|overdose|rope|knife|gun|poison)\b",
]

def _match_any(patterns: List[str], text: str) -> bool:
    """Check if any pattern matches the text"""
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)

def get_flags(text: str) -> List[str]:
    """Extract safety flags from text based on pattern matching"""
    flags = []
    if _match_any(INTENT_PATTERNS, text):
        flags.append("intent")
    if _match_any(TIME_PATTERNS, text):
        flags.append("time")
    if _match_any(PLAN_PATTERNS, text):
        flags.append("plan")
    if _match_any(MEANS_PATTERNS, text):
        flags.append("means")
    
    if flags:
        logger.warning(f"Safety flags detected: {flags}")
    
    return flags

def decide_action(risk_label: str, confidence: float, flags: List[str]) -> str:
    """Determine recommended action based on risk assessment"""
    # Highest severity based on rules (plan/intent/time)
    if ("intent" in flags and "time" in flags) or \
       ("plan" in flags and ("intent" in flags or "time" in flags)):
        logger.critical("Critical crisis indicators detected")
        return "crisis_critical"

    # If any flag exists, treat as high risk
    if flags:
        logger.error("High risk indicators detected")
        return "crisis_high"

    # If model says suicidal, treat as high risk
    if str(risk_label).lower() in ["suicidal", "suicide"]:
        logger.error("Model predicted suicidal risk")
        return "crisis_high"

    # If model confidence is low, respond safely
    if confidence < 0.55:
        logger.warning(f"Low confidence prediction: {confidence}")
        return "uncertain_support"

    return "normal"

# =============================================================================
# Request/Response schemas
# =============================================================================
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000, description="Text to analyze")
    context: Optional[List[str]] = Field(None, description="Optional conversation context")

class AnalyzeResponse(BaseModel):
    risk_label: str = Field(..., description="Predicted risk category")
    confidence: float = Field(..., description="Model confidence score")
    flags: List[str] = Field(..., description="Detected safety flags")
    recommended_action: str = Field(..., description="Recommended response action")

# =============================================================================
# Routes
# =============================================================================
@app.get("/health")
def health_check():
    """Health check endpoint"""
    if not settings.HEALTH_CHECK_ENABLED:
        raise HTTPException(status_code=404, detail="Health check disabled")
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENV
    }

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """
    Analyze text for mental health risk indicators
    
    Args:
        req: AnalyzeRequest with text and optional context
        
    Returns:
        AnalyzeResponse with risk assessment
    """
    try:
        text = req.text.strip()
        logger.info("Received analysis request", extra={
            "text_length": len(text),
            "has_context": req.context is not None
        })

        # 1) Extract rule-based flags
        flags = get_flags(text)

        # 2) Model prediction
        try:
            # Transform text with vectorizer if available
            if vectorizer is not None:
                text_vectorized = vectorizer.transform([text])
            else:
                text_vectorized = [text]
            
            if not hasattr(model, "predict_proba"):
                # Fallback for models without predict_proba
                pred = model.predict(text_vectorized)[0]
                risk_label = str(pred)
                confidence = 1.0
            else:
                proba = model.predict_proba(text_vectorized)[0]
                best_idx = int(proba.argmax())
                confidence = float(proba[best_idx])

                # Use labels.json if available, otherwise model.classes_
                if labels is not None:
                    risk_label = str(labels[best_idx])
                elif hasattr(model, "classes_"):
                    risk_label = str(model.classes_[best_idx])
                else:
                    risk_label = str(best_idx)
            
            logger.info("Model prediction completed", extra={
                "risk_label": risk_label,
                "confidence": confidence
            })
            
        except Exception as e:
            logger.error(f"Model prediction failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Model prediction failed"
            )

        # 3) Decide action
        action = decide_action(risk_label, confidence, flags)
        
        logger.info("Analysis completed", extra={
            "risk_label": risk_label,
            "confidence": confidence,
            "flags": flags,
            "action": action
        })

        return AnalyzeResponse(
            risk_label=risk_label,
            confidence=confidence,
            flags=flags,
            recommended_action=action,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# =============================================================================
# Startup/Shutdown events
# =============================================================================
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("Application startup complete")
    
    # Validate configuration in production
    if settings.is_production():
        try:
            settings.validate()
        except ValueError as e:
            logger.critical(f"Configuration validation failed: {str(e)}")
            raise

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Application shutting down")
