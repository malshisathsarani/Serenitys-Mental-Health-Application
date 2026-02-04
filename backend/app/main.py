"""
Serenity Mental Health API
Production-ready FastAPI application with ML integration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import health, ml, chat
from app.services.ml_service import get_ml_service

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered mental health analysis API",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
logger.info(f"Environment: {settings.ENV}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Application startup initiated")
    
    try:
        # Initialize ML service (loads model)
        ml_service = get_ml_service()
        logger.info("ML Service initialized successfully")
        logger.info(f"Model classes: {ml_service.classes}")
        
    except FileNotFoundError as e:
        logger.error(f"Model not found: {e}")
        logger.error("Please train the model first: cd ml && python train.py")
        raise
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Application shutdown initiated")


# Include routers
app.include_router(health.router)
app.include_router(ml.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


# Run application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
