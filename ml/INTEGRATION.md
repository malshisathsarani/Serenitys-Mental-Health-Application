# ML Module Integration Guide

## 🎯 Integration with Backend API

This guide explains how to integrate the ML module with your FastAPI backend.

## Option 1: Direct Import (Recommended for Development)

### Step 1: Update Backend Dependencies

Add to `backend/requirements.txt`:

```
scikit-learn==1.4.0
joblib==1.3.2
```

### Step 2: Create ML Service in Backend

Create `backend/app/services/ml_service.py`:

```python
import joblib
from pathlib import Path

class MLService:
    def __init__(self):
        # Path to ML models (adjust based on your structure)
        ml_root = Path(__file__).parent.parent.parent.parent / "ml"
        model_path = ml_root / "models" / "text_classifier.joblib"

        # Load model
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.vectorizer = model_data['vectorizer']
        self.classes = model_data['classes']

    def predict(self, text: str):
        """Predict mental health status from text"""
        X = self.vectorizer.transform([text])
        prediction = self.model.predict(X)[0]

        # Get probabilities
        probabilities = {}
        if hasattr(self.model, 'predict_proba'):
            probs = self.model.predict_proba(X)[0]
            probabilities = {
                label: float(prob)
                for label, prob in zip(self.classes, probs)
            }

        return {
            "prediction": prediction,
            "probabilities": probabilities
        }

# Create singleton instance
ml_service = MLService()
```

### Step 3: Add API Endpoint

In `backend/app/main.py` or create `backend/app/routers/ml.py`:

```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ml_service import ml_service

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])

class TextInput(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    prediction: str
    probabilities: dict

@router.post("/predict", response_model=PredictionResponse)
async def predict_mental_health(input_data: TextInput):
    """Predict mental health status from text"""
    result = ml_service.predict(input_data.text)
    return result
```

### Step 4: Register Router

In `backend/app/main.py`:

```python
from app.routers import ml

app.include_router(ml.router)
```

## Option 2: Separate ML Service (Recommended for Production)

### Create Standalone ML API

Create `ml/api/main.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
import sys
from pathlib import Path

# Add ML module to path
ml_root = Path(__file__).parent.parent
sys.path.insert(0, str(ml_root))

from scripts.predict import MentalHealthPredictor

app = FastAPI(title="Serenity ML API")
predictor = MentalHealthPredictor()
predictor.load_model()

class TextInput(BaseModel):
    text: str

@app.post("/predict")
async def predict(input_data: TextInput):
    prediction, probabilities = predictor.predict(input_data.text)
    return {
        "prediction": prediction,
        "probabilities": probabilities
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

Run ML service separately:

```bash
cd ml/api
uvicorn main:app --port 8001
```

Call from main backend:

```python
import httpx

async def get_ml_prediction(text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/predict",
            json={"text": text}
        )
        return response.json()
```

## Option 3: Use ML Module Directly

### In Backend Code

```python
import sys
from pathlib import Path

# Add ML module to path
ml_path = Path(__file__).parent.parent.parent / "ml"
sys.path.insert(0, str(ml_path))

from scripts.predict import MentalHealthPredictor

# Initialize predictor
predictor = MentalHealthPredictor()
predictor.load_model()

# Use in your endpoint
@app.post("/analyze")
async def analyze_text(text: str):
    prediction, probabilities = predictor.predict(text)
    return {
        "status": prediction,
        "confidence": probabilities
    }
```

## Testing the Integration

### Test with curl:

```bash
curl -X POST http://localhost:8000/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel anxious and stressed today"}'
```

### Test with Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/ml/predict",
    json={"text": "I feel anxious and stressed today"}
)

print(response.json())
# Output: {"prediction": "Stress", "probabilities": {...}}
```

## Production Considerations

### 1. Model Loading

- Load model once at startup (not per request)
- Use dependency injection for model service
- Implement model versioning

### 2. Performance

- Add caching for frequent predictions
- Use async operations
- Consider batch prediction endpoint

### 3. Monitoring

- Log all predictions
- Track prediction latency
- Monitor model performance

### 4. Security

- Validate input text (length, content)
- Rate limiting on ML endpoints
- Authentication/authorization

### 5. Model Updates

- Implement model version management
- Hot-reload new models without downtime
- A/B testing for model comparison

## Example Full Integration

```python
# backend/app/services/ml_service.py
import joblib
import logging
from pathlib import Path
from typing import Dict, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)

class MLService:
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
        ml_root = Path(__file__).parent.parent.parent.parent / "ml"
        model_path = ml_root / "models" / "text_classifier.joblib"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.vectorizer = model_data['vectorizer']
        self.classes = model_data['classes']

        logger.info("ML Service initialized successfully")
        self._initialized = True

    def predict(self, text: str) -> Dict:
        """Predict mental health status"""
        try:
            X = self.vectorizer.transform([text])
            prediction = self.model.predict(X)[0]

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
            logger.error(f"Prediction error: {str(e)}")
            return {
                "prediction": None,
                "probabilities": {},
                "status": "error",
                "message": str(e)
            }

# Singleton instance
@lru_cache()
def get_ml_service() -> MLService:
    return MLService()
```

```python
# backend/app/routers/ml.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from app.services.ml_service import get_ml_service, MLService

router = APIRouter(prefix="/api/ml", tags=["ML"])

class TextInput(BaseModel):
    text: str

    @validator('text')
    def validate_text(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Text must be at least 10 characters')
        if len(v) > 5000:
            raise ValueError('Text must be less than 5000 characters')
        return v.strip()

@router.post("/predict")
async def predict(
    input_data: TextInput,
    ml_service: MLService = Depends(get_ml_service)
):
    """Predict mental health status from text"""
    result = ml_service.predict(input_data.text)

    if result['status'] == 'error':
        raise HTTPException(status_code=500, detail=result['message'])

    return result

@router.get("/health")
async def health_check():
    """Check ML service health"""
    return {"status": "healthy", "service": "ml"}
```

This integration provides a robust, production-ready connection between your ML module and backend! 🚀
