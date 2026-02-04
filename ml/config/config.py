"""
ML Configuration Module
Centralized configuration for all ML components
"""
import os
from pathlib import Path
from typing import Dict, Any

# Base directories
ML_ROOT = Path(__file__).parent.parent
DATA_DIR = ML_ROOT / "data"
MODELS_DIR = ML_ROOT / "models"
LOGS_DIR = ML_ROOT / "logs"

# Data subdirectories
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model configurations
MODEL_CONFIG: Dict[str, Any] = {
    "text_classifier": {
        "model_type": "logistic_regression",
        "max_features": 20000,
        "max_iter": 3000,
        "class_weight": "balanced",
        "random_state": 42
    }
}

# Training configurations
TRAINING_CONFIG: Dict[str, Any] = {
    "test_size": 0.2,
    "random_state": 42,
    "validation_split": 0.1
}

# Data preprocessing configurations
PREPROCESSING_CONFIG: Dict[str, Any] = {
    "text_column": "text",
    "label_column": "status",
    "min_text_length": 10,
    "remove_duplicates": True
}

# Paths
DEFAULT_DATASET = DATA_DIR / "raw" / "dataset.csv"
TRAINED_MODEL_PATH = MODELS_DIR / "text_classifier.joblib"
LABELS_PATH = MODELS_DIR / "labels.json"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
