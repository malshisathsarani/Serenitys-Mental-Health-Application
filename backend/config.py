"""
Configuration management for the Mental Health API
Loads settings from environment variables with fallbacks
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
    BASE_DIR: Path = Path(__file__).resolve().parent
    ROOT_DIR: Path = BASE_DIR
    
    # Application
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    APP_NAME: str = os.getenv("APP_NAME", "Mental Health Risk API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Paths
    MODEL_DIR: Path = BASE_DIR / os.getenv("MODEL_DIR", "models")
    DATA_DIR: Path = BASE_DIR / os.getenv("DATA_DIR", "data")
    LOGS_DIR: Path = BASE_DIR / os.getenv("LOGS_DIR", "logs")
    
    # Model files
    MODEL_FILE: str = os.getenv("MODEL_FILE", "text_classifier.joblib")
    LABELS_FILE: str = os.getenv("LABELS_FILE", "labels.json")
    
    # Full paths to model files
    MODEL_PATH: Path = MODEL_DIR / MODEL_FILE
    LABELS_PATH: Path = MODEL_DIR / LABELS_FILE
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Health check
    HEALTH_CHECK_ENABLED: bool = os.getenv("HEALTH_CHECK_ENABLED", "True").lower() == "true"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
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
            errors.append(f"Model file not found: {cls.MODEL_PATH}")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.ensure_directories()
