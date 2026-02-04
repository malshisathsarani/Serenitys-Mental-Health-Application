"""
ML Service
Integration with the ML module for predictions
"""
import joblib
import logging
from pathlib import Path
from typing import Dict, Tuple
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)


class MLService:
    """Service for ML model integration"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        logger.info("Initializing ML Service...")
        
        # Check if model exists
        if not settings.MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {settings.MODEL_PATH}. "
                f"Please train the model first: cd ml && python train.py"
            )
        
        # Load model
        model_data = joblib.load(settings.MODEL_PATH)
        self.model = model_data['model']
        self.vectorizer = model_data['vectorizer']
        self.classes = model_data['classes']
        
        logger.info(f"ML Service initialized successfully. Classes: {self.classes}")
        self._initialized = True
    
    def predict(self, text: str) -> Dict:
        """
        Predict mental health status from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with prediction and probabilities
        """
        try:
            # Vectorize input
            X = self.vectorizer.transform([text])
            
            # Make prediction
            prediction = self.model.predict(X)[0]
            
            # Get probabilities
            probabilities = {}
            if hasattr(self.model, 'predict_proba'):
                probs = self.model.predict_proba(X)[0]
                probabilities = {
                    label: float(prob) 
                    for label, prob in zip(self.classes, probs)
                }
            
            logger.info(f"Prediction made: {prediction}")
            
            return {
                "prediction": prediction,
                "probabilities": probabilities,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            return {
                "prediction": None,
                "probabilities": {},
                "status": "error",
                "message": str(e)
            }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            "classes": self.classes,
            "model_type": type(self.model).__name__,
            "vocabulary_size": len(self.vectorizer.vocabulary_),
            "model_path": str(settings.MODEL_PATH)
        }


# Singleton instance getter
@lru_cache()
def get_ml_service() -> MLService:
    """Get ML service instance (cached)"""
    return MLService()
