from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import joblib
import json
import re

# =============================================================================
# App
# =============================================================================
app = FastAPI(title="Mental Health Risk API", version="1.0")

# =============================================================================
# Paths (FIXED)
# mental_health_training/
#   backend/
#     main.py
#   models/
#     text_classifier.joblib
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent  # Go up to mental_health_training
MODEL_DIR = BASE_DIR / "models"

MODEL_JOBLIB = MODEL_DIR / "text_classifier.joblib"
MODEL_PKL = MODEL_DIR / "mental_health_model.pkl"
LABELS_JSON = MODEL_DIR / "labels.json"

# =============================================================================
# Load model (supports joblib or pkl)
# =============================================================================
def load_model_and_labels():
    if MODEL_JOBLIB.exists():
        model_path = MODEL_JOBLIB
    elif MODEL_PKL.exists():
        model_path = MODEL_PKL
    else:
        raise FileNotFoundError(
            f"Model file not found.\n"
            f"Expected one of:\n"
            f"- {MODEL_JOBLIB}\n"
            f"- {MODEL_PKL}\n\n"
            f"Put your model file inside: {MODEL_DIR}"
        )

    print(f"[INFO] Loading model from: {model_path}")
    model_data = joblib.load(model_path)
    
    # Handle both formats: dict with model/vectorizer or just the model
    if isinstance(model_data, dict):
        model = model_data.get("model")
        vectorizer = model_data.get("vectorizer")
        print(f"[INFO] Loaded model and vectorizer from combined file")
    else:
        model = model_data
        vectorizer = None
        print(f"[INFO] Loaded model only")

    labels = None
    if LABELS_JSON.exists():
        labels = json.loads(LABELS_JSON.read_text(encoding="utf-8"))
        print(f"[INFO] Loaded labels from: {LABELS_JSON}")
        print(f"[INFO] Labels: {labels}")
    else:
        print("[WARN] labels.json not found. Will use model.classes_ if available.")

    return model, vectorizer, labels

model, vectorizer, labels = load_model_and_labels()

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
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)

def get_flags(text: str) -> List[str]:
    flags = []
    if _match_any(INTENT_PATTERNS, text):
        flags.append("intent")
    if _match_any(TIME_PATTERNS, text):
        flags.append("time")
    if _match_any(PLAN_PATTERNS, text):
        flags.append("plan")
    if _match_any(MEANS_PATTERNS, text):
        flags.append("means")
    return flags

def decide_action(risk_label: str, confidence: float, flags: List[str]) -> str:
    # Highest severity based on rules (plan/intent/time)
    if ("intent" in flags and "time" in flags) or ("plan" in flags and ("intent" in flags or "time" in flags)):
        return "crisis_critical"

    # If any flag exists, treat as high risk
    if flags:
        return "crisis_high"

    # If model says suicidal, treat as high risk
    if str(risk_label).lower() in ["suicidal", "suicide"]:
        return "crisis_high"

    # If model confidence is low, respond safely
    if confidence < 0.55:
        return "uncertain_support"

    return "normal"

# =============================================================================
# Request/Response schemas
# =============================================================================
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    context: Optional[List[str]] = None  # optional last messages

class AnalyzeResponse(BaseModel):
    risk_label: str
    confidence: float
    flags: List[str]
    recommended_action: str

# =============================================================================
# Routes
# =============================================================================
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    text = req.text.strip()

    # 1) Rule flags
    flags = get_flags(text)

    # 2) Model prediction (must support predict_proba)
    # Transform text with vectorizer if available
    if vectorizer is not None:
        text_vectorized = vectorizer.transform([text])
    else:
        text_vectorized = [text]
    
    if not hasattr(model, "predict_proba"):
        # Some sklearn models might not have predict_proba
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

    # 3) Decide app action
    action = decide_action(risk_label, confidence, flags)

    return AnalyzeResponse(
        risk_label=risk_label,
        confidence=confidence,
        flags=flags,
        recommended_action=action,
    )