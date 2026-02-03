"""
Unit Tests for Configuration Module
"""
import pytest
from pathlib import Path
import os
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import Settings

class TestSettings:
    """Test configuration settings"""
    
    def test_default_values(self):
        """Test that default values are set correctly"""
        settings = Settings()
        assert settings.ENV in ["development", "production", "test"]
        assert settings.APP_NAME == "Mental Health Risk API"
        assert settings.PORT == 8000
    
    def test_paths_exist(self):
        """Test that base paths are valid"""
        settings = Settings()
        assert settings.BASE_DIR.exists()
        assert isinstance(settings.MODEL_DIR, Path)
        assert isinstance(settings.DATA_DIR, Path)
    
    def test_ensure_directories(self):
        """Test directory creation"""
        settings = Settings()
        settings.ensure_directories()
        assert settings.MODEL_DIR.exists()
        assert settings.DATA_DIR.exists()
        assert settings.LOGS_DIR.exists()
    
    def test_is_production(self):
        """Test production detection"""
        settings = Settings()
        # Default should not be production
        is_prod = settings.is_production()
        assert isinstance(is_prod, bool)
    
    def test_environment_variables(self, monkeypatch):
        """Test that environment variables are loaded"""
        monkeypatch.setenv("PORT", "9000")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        settings = Settings()
        assert settings.PORT == 9000
        assert settings.LOG_LEVEL == "DEBUG"
