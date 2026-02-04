"""
Core Configuration Module
Application settings and configuration management
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    ROOT_DIR: Path = BASE_DIR
    
    # ML Module path (separate from backend)
    ML_DIR: Path = BASE_DIR.parent / "ml"
    ML_MODELS_DIR: Path = ML_DIR / "models"
    ML_DATA_DIR: Path = ML_DIR / "data"
    
    # Application
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    APP_NAME: str = os.getenv("APP_NAME", "Serenity Mental Health API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Backend-specific paths
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # ML Model files (now pointing to ml/ folder)
    MODEL_FILE: str = os.getenv("MODEL_FILE", "text_classifier.joblib")
    LABELS_FILE: str = os.getenv("LABELS_FILE", "labels.json")
    
    # Full paths to ML model files
    MODEL_PATH: Path = ML_MODELS_DIR / MODEL_FILE
    LABELS_PATH: Path = ML_MODELS_DIR / LABELS_FILE
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8081",  # Flutter web
    ]
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Health check
    HEALTH_CHECK_ENABLED: bool = os.getenv("HEALTH_CHECK_ENABLED", "True").lower() == "true"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary backend directories if they don't exist"""
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENV.lower() == "production"
    
    @classmethod
    def validate(cls):
        """Validate critical settings"""
        errors = []
        
        if cls.is_production() and cls.SECRET_KEY == "dev-secret-key-change-in-production":
            errors.append("SECRET_KEY must be changed in production")
        
        if not cls.MODEL_PATH.exists():
            errors.append(
                f"Model file not found: {cls.MODEL_PATH}. "
                f"Please train the model first using: cd ml && python train.py"
            )
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.ensure_directories()
