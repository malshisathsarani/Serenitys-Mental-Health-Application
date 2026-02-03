"""
Logging configuration for the Mental Health API
"""
import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger
from config import settings


def setup_logging():
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(
        settings.LOGS_DIR / "app.log",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    
    # Format based on configuration
    if settings.LOG_FORMAT == "json":
        # JSON format for production
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level"}
        )
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Log startup
    logger.info(
        "Logging configured",
        extra={
            "env": settings.ENV,
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT
        }
    )
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(name)
