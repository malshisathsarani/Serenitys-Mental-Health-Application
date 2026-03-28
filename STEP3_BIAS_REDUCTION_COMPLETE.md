# 🎯 STEP 3: Bias Reduction Learning Loop - Implementation Guide

## Overview

**Serenity Mental Health Application** now includes automated bias detection and model improvement through user feedback. This is **STEP 3 of 4** in the project completion roadmap.

### What's New

The system automatically:

1. ✅ Collects user feedback on AI responses (helpful/unhelpful)
2. ✅ Identifies biased/incorrect prediction patterns
3. ✅ Calculates fairness metrics by prediction type
4. ✅ Retrains ML model with feedback-corrected data
5. ✅ Tracks model performance improvements over time

---

## Architecture

### Data Flow

```
User sends feedback (helpful/unhelpful)
    ↓
MessageFeedback table stores feedback
    ↓
FeedbackProcessor extracts biased responses
    ├─ Identifies correction pattern (e.g., "Normal → Suicidal")
    ├─ Groups by prediction type for bias analysis
    └─ Returns training dataset with corrected labels
    ↓
ModelRetrainer combines:
    ├─ Original training data (70% by default)
    ├─ Feedback corrections (30%)
    └─ Retrains TF-IDF + Logistic Regression
    ↓
New model version saved with metrics & backups
    ↓
API returns performance improvement summary
```

---

## Components

### 1. Feedback Processor Service

**File:** `backend/app/services/feedback_processor.py`

**Responsibilities:**

- Extract unhelpful feedback from database
- Link feedback to original user input and predictions
- Infer corrected labels from feedback comments
- Group bias patterns (e.g., "Anxiety → Suicidal" occurs 5 times)
- Calculate fairness metrics by prediction category

**Key Methods:**

```python
# Extract biased responses for retraining
await feedback_processor.extract_feedback_training_data(
    db_session=db,
    days_ago=30,  # Only feedback from last 30 days
    min_feedback_count=0
)

# Get fairness metrics
await feedback_processor.calculate_bias_metrics(
    db_session=db,
    prediction_category="Suicidal"  # Optional filter
)
```

### 2. Model Retrainer Service

**File:** `backend/app/services/model_retrainer.py`

**Responsibilities:**

- Load original training data
- Mix with feedback-corrected data (weighted sampling)
- Train new TF-IDF vectorizer + Logistic Regression
- Backup old model
- Save new model with version metadata
- Calculate comprehensive metrics

**Key Methods:**

```python
# Retrain with feedback data
await retrainer.retrain_with_feedback(
    feedback_texts=["I'm feeling suicidal", ...],
    feedback_labels=["Suicidal", ...],
    mix_ratio=0.7  # 70% original, 30% feedback
)

# Compare with previous version
await retrainer.compare_models()
```

### 3. Training API Routes

**File:** `backend/app/api/routes/training.py`

**Endpoints:**

| Endpoint                         | Method | Purpose                                       |
| -------------------------------- | ------ | --------------------------------------------- |
| `/api/training/feedback-summary` | GET    | View bias patterns from user feedback         |
| `/api/training/bias-metrics`     | GET    | Calculate fairness metrics by prediction type |
| `/api/training/retrain-model`    | POST   | Trigger model retraining with feedback        |
| `/api/training/model-versions`   | GET    | View history of trained model versions        |
| `/api/training/compare-models`   | POST   | Compare current vs previous model             |

---

## Usage

### 1. Collect Feedback (Phase 1)

Users rate responses as helpful/unhelpful in the app:

```dart
// From flutter app
_submitMessageFeedback(
  messageId: response.assistantMessageId,
  helpful: false,  // Marked as unhelpful
  comment: "This is completely wrong - I'm suicidal, not just anxious"
)

// POST /api/feedback
{
  "message_id": 42,
  "helpful": false,
  "comment": "This is completely wrong - I'm suicidal, not just anxious"
}
```

### 2. View Bias Metrics

After collecting enough feedback, check fairness metrics:

```bash
curl http://localhost:8000/api/training/bias-metrics
```

Response:

```json
{
  "status": "success",
  "metrics": {
    "metrics_by_prediction": {
      "Suicidal": {
        "total": 15,
        "helpful": 12,
        "unhelpful": 3,
        "helpful_rate": 0.8,
        "confidence_avg": 0.92
      },
      "Anxiety": {
        "total": 20,
        "helpful": 10,
        "unhelpful": 10,
        "helpful_rate": 0.5,
        "confidence_avg": 0.65
      }
    },
    "concerning_categories": {
      "Anxiety": { "helpful_rate": 0.5, "total": 20 }
    },
    "recommendation": "Anxiety prediction has low helpful rate (50%) - needs retraining"
  }
}
```

### 3. Trigger Model Retraining

When sufficient feedback is collected (recommendation: ≥5 unhelpful feedbacks):

```bash
curl -X POST http://localhost:8000/api/training/retrain-model \
  -H "Content-Type: application/json" \
  -d '{
    "min_feedback_days": 7,
    "mix_original_ratio": 0.7
  }'
```

Response:

```json
{
  "status": "success",
  "message": "Model retrained successfully with 8 feedback corrections",
  "version": "2026-03-28T14:30:00.000000",
  "metrics": {
    "accuracy": 0.8412,
    "macro_f1": 0.7924,
    "weighted_f1": 0.8356,
    "per_class": {
      "Suicidal": { "precision": 0.92, "recall": 0.88, "f1": 0.9 },
      "Anxiety": { "precision": 0.76, "recall": 0.82, "f1": 0.79 }
    }
  },
  "training_summary": {
    "total_samples": 728,
    "feedback_samples": 8,
    "original_samples": 720,
    "train_test_split": "582/146"
  },
  "bias_analysis": {
    "patterns": {
      "Anxiety → Suicidal": 3,
      "Normal → Depression": 2,
      "Depression → Suicidal": 2,
      "Normal → Suicidal": 1
    },
    "most_common_bias": "Anxiety → Suicidal"
  },
  "model_comparison": {
    "current_accuracy": 0.8412,
    "previous_accuracy": 0.8105,
    "accuracy_improvement": 0.0307
  }
}
```

### 4. View Model Versions

Track model evolution:

```bash
curl http://localhost:8000/api/training/model-versions
```

Response:

```json
{
  "status": "success",
  "total_versions": 2,
  "versions": [
    {
      "version": "2026-03-26T10:15:00",
      "training_samples": 720,
      "feedback_samples": 0,
      "test_accuracy": 0.8105,
      "metrics": {...}
    },
    {
      "version": "2026-03-28T14:30:00",
      "training_samples": 728,
      "feedback_samples": 8,
      "test_accuracy": 0.8412,
      "metrics": {...}
    }
  ]
}
```

---

## Database Schema

### MessageFeedback Table

Already created in STEP 2:

```sql
CREATE TABLE message_feedback (
  id INT PRIMARY KEY AUTO_INCREMENT,
  message_id INT NOT NULL FOREIGN KEY,
  user_id INT NOT NULL FOREIGN KEY,
  helpful BOOLEAN NOT NULL,         -- User rated helpful/unhelpful
  comment TEXT,                      -- Optional feedback reason
  created_at DATETIME DEFAULT NOW(),
  INDEX idx_feedback_message_user (message_id, user_id),
  INDEX idx_feedback_created_at (created_at)
);
```

---

## Workflow: Weekly Bias Reduction Loop

### Monday: Collect Feedback

Users submit feedback throughout the week as they interact with the chatbot.

### Friday: Analysis

```bash
# Check bias metrics
curl http://localhost:8000/api/training/bias-metrics

# Get feedback summary
curl http://localhost:8000/api/training/feedback-summary?days=7
```

### Saturday: Retrain

If ≥5 unhelpful feedbacks detected:

```bash
curl -X POST http://localhost:8000/api/training/retrain-model \
  -H "Content-Type: application/json"

# Review new metrics
curl http://localhost:8000/api/training/model-versions
```

### Deploy

If accuracy improved ≥1%:

- Old model automatically backed up to `ml/models/backups/`
- New model immediately active
- Version metadata saved to `ml/models/versions.json`

---

## Bias Correction Strategy

### How Corrected Labels Are Inferred

When processing unhelpful feedback:

1. **From comment keywords:**
   - Suicide indicators: "suicidal", "kill myself", "harm", "crisis" → Label: **Suicidal**
   - Anxiety indicators: "anxiety", "panic", "worry", "nervous" → Label: **Anxiety**
   - Depression indicators: "sad", "hopeless", "depressed", "worthless" → Label: **Depression**
   - Normal: "fine", "okay", "good", "happy" → Label: **Normal**

2. **No keywords provided:**
   - Default to opposite of current prediction
   - Assumes if prediction was wrong, try alternative

### Bias Pattern Examples

```
User input: "I'm so scared I can't breathe"
Original prediction: "Normal" (WRONG)
User feedback: "This is clearly anxiety"
Corrected label: "Anxiety"
Pattern recorded: "Normal → Anxiety"

---

User input: "I want to end my life"
Original prediction: "Depression" (PARTIALLY CORRECT)
User feedback: "This is immediate suicide risk, not depression"
Corrected label: "Suicidal"
Pattern recorded: "Depression → Suicidal"
```

---

## Performance Metrics

### Per-Class Metrics Tracked

For each prediction category (Suicidal, Anxiety, Depression, Normal):

- **Precision:** How many predicted positive are actually positive
- **Recall:** How many actual positives were correctly identified
- **F1-Score:** Harmonic mean of precision and recall
- **Helpful Rate:** From feedback (% of users found responses helpful)

### Overall Metrics

- **Accuracy:** Overall correct predictions
- **Macro F1:** Average F1 across all classes
- **Weighted F1:** F1 weighted by class frequency

### Bias Indicators

Categories with <60% helpful rate and ≥5 feedback samples flagged as concerning.

---

## Model Versioning

### Version Metadata

Each trained model saved with:

```json
{
  "version": "2026-03-28T14:30:00.000000",
  "training_samples": 728,
  "feedback_samples": 8,
  "original_samples": 720,
  "mix_ratio_original": 0.7,
  "test_accuracy": 0.8412,
  "metrics": {
    "accuracy": 0.8412,
    "macro_f1": 0.7924,
    "per_class": {...}
  }
}
```

### Version History

Last 10 versions kept in `ml/models/versions.json`:

```json
[
  { "version": "v1", "accuracy": 0.81 },
  { "version": "v2", "accuracy": 0.82 },
  { "version": "v3", "accuracy": 0.84 } // Latest
]
```

### Model Backup

Previous model automatically backed up:

- Location: `ml/models/backups/model_backup_20260328_143000.joblib`
- Allows rollback if new model performs worse

---

## Integration with Existing Components

### Chat Route Enhancement

When crisis detected (from STEP 2):

```python
# chat.py - Already implemented
if crisis_detected:
    emergency_call_result = await emergency_service.trigger_emergency_call(...)

# New in STEP 3: Also log for feedback
message.crisis_detected = crisis_detected
message.probabilities = result.get("probabilities")
message.prediction = result.get("prediction")

await db.commit()
```

### Feedback Collection (Flutter)

```dart
// chat_screen.dart - Already implemented
_submitMessageFeedback(
  messageId: message.serverAssistantMessageId,
  helpful: helpful,  // User votes
  comment: comment   // User reason
)
```

### Retraining Trigger (Automation)

Can be triggered:

1. **Manual:** Via API endpoint
2. **Scheduled:** Cron job daily/weekly
3. **Threshold-based:** Auto-trigger after ≥10 unhelpful feedbacks

---

## Configuration

### Retraining Parameters

In `backend/app/core/config.py`:

```python
# Feedback processing
FEEDBACK_MIN_SAMPLES = 5           # Minimum to retrain
FEEDBACK_LOOKBACK_DAYS = 30        # How far back to look
FEEDBACK_HELPFUL_THRESHOLD = 0.6   # Flag if <60% helpful

# Retraining
ML_MIX_RATIO_ORIGINAL = 0.7        # Keep 70% original data
MODEL_BACKUP_RETENTION = 10        # Keep last N versions
MODEL_AUTO_RELOAD = True           # Reload after retraining
```

---

## Testing

### Unit Tests

**File:** `backend/tests/test_feedback_processor.py`

```bash
pytest backend/tests/test_feedback_processor.py -v

test_infer_corrected_label_suicidal - PASSED
test_infer_corrected_label_anxiety - PASSED
test_infer_corrected_label_depression - PASSED
test_bias_pattern_identification - PASSED
```

### Integration Testing

1. Submit feedback via API → verify saved to DB
2. Extract feedback → verify correct bias patterns
3. Retrain model → verify new model created
4. Check versions → verify metadata saved
5. Compare models → verify accuracy reported

---

## Next Steps

### Immediate (This Sprint)

- ✅ Implement bias detection pipeline
- ✅ Create feedback processing service
- ✅ Implement model retraining
- ✅ Create training API endpoints
- ⏳ **Testing and validation**
- ⏳ **Deploy and monitor**

### Future Enhancements

- **Automated Retraining:** Schedule daily at 2 AM
- **A/B Testing:** Compare model versions on real traffic
- **Demographic Parity:** Track fairness across age/gender groups (if available)
- **Explanation Generation:** Why was this response marked unhelpful?
- **Model Card:** Document model limitations and bias analysis
- **Dashboard:** Real-time bias metrics visualization

---

## Troubleshooting

### "No unhelpful feedback found"

- **Cause:** Not enough users have marked responses as unhelpful
- **Solution:** Increase `days_ago` parameter or wait for more feedback

### "Retraining accuracy worse than previous"

- **Cause:** Feedback data contradictory or training data too small
- **Solution:** Try reducing `mix_original_ratio` to keep more original data

### "Model not loading after retraining"

- **Cause:** Corrupted joblib file or incompatible scikit-learn version
- **Solution:** Check `ml/models/backups/` for previous version, roll back manually

---

## Key Files

| File                                         | Purpose                      |
| -------------------------------------------- | ---------------------------- |
| `backend/app/services/feedback_processor.py` | Extract and analyze feedback |
| `backend/app/services/model_retrainer.py`    | Retrain model with feedback  |
| `backend/app/api/routes/training.py`         | API endpoints for retraining |
| `backend/tests/test_feedback_processor.py`   | Unit tests                   |
| `ml/models/versions.json`                    | Model version history        |
| `ml/models/backups/`                         | Previous model versions      |

---

**Status:** ✅ STEP 3 IMPLEMENTED

**Next:** STEP 4 - Documentation & Cleanup

---

## FYP Project Novelty Claim

This bias reduction learning loop demonstrates:

✅ **Continuous Learning:** Model improves from user feedback  
✅ **Fairness Monitoring:** Tracks bias metrics by category  
✅ **Automated Retraining:** Processes feedback → retrains → validates  
✅ **Version Control:** Maintains model evolution history  
✅ **Production Readiness:** Backups, rollback, metrics tracking

This addresses the FYP requirement for **adaptive AI systems that learn from corrections and improve fairness over time**.
