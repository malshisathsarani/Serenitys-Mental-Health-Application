"""
Training API Routes - STEP 3 Bias Reduction
Endpoints for model retraining using feedback data.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.services.feedback_processor import (
    get_feedback_processor,
    FeedbackProcessor,
)
from app.services.model_retrainer import get_model_retrainer, ModelRetrainer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/training", tags=["Training & Bias"])


@router.get("/feedback-summary")
async def get_feedback_summary(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    processor: FeedbackProcessor = Depends(get_feedback_processor),
):
    """
    Get summary of user feedback for bias analysis.
    
    Returns:
    - Total helpful/unhelpful responses in last N days
    - Bias patterns (prediction → corrected_to)
    - Most common areas of model error
    """
    try:
        feedback_data = await processor.extract_feedback_training_data(
            db_session=db,
            days_ago=days,
        )
        
        return {
            "status": "success",
            "days_analyzed": days,
            "feedback_data": feedback_data,
        }
    except Exception as e:
        logger.error(f"Error getting feedback summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bias-metrics")
async def get_bias_metrics(
    prediction_category: str = None,
    db: AsyncSession = Depends(get_db),
    processor: FeedbackProcessor = Depends(get_feedback_processor),
):
    """
    Calculate fairness/bias metrics from current feedback.
    
    Metrics:
    - Helpful rate by prediction type
    - False positive/negative analysis
    - Concerning categories (<60% helpful with ≥5 feedback)
    - Recommendation for improvement
    
    Args:
        prediction_category: Optional filter (e.g., "Suicidal")
    """
    try:
        metrics = await processor.calculate_bias_metrics(
            db_session=db,
            prediction_category=prediction_category,
        )
        
        return {
            "status": "success",
            "metrics": metrics,
        }
    except Exception as e:
        logger.error(f"Error calculating bias metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain-model")
async def retrain_model_endpoint(
    min_feedback_days: int = 7,
    mix_original_ratio: float = 0.7,
    db: AsyncSession = Depends(get_db),
    processor: FeedbackProcessor = Depends(get_feedback_processor),
    retrainer: ModelRetrainer = Depends(get_model_retrainer),
):
    """
    Trigger model retraining using collected feedback data.
    
    Flow:
    1. Extract biased responses from feedback (last N days)
    2. If sufficient feedback exists, combine with original data
    3. Retrain TF-IDF + Logistic Regression
    4. Backup old model, save new model with version metadata
    5. Return performance metrics
    
    Args:
        min_feedback_days: Only use feedback from last N days
        mix_original_ratio: Ratio of original training data to keep (0.0-1.0)
        
    Response:
        - status: success/error
        - metrics: test accuracy, F1, per-class performance
        - version: timestamp of new model
        - improvement: comparison with previous model
    """
    try:
        logger.info(f"Starting model retraining (mix_ratio={mix_original_ratio})")
        
        # Step 1: Extract feedback
        feedback_data = await processor.extract_feedback_training_data(
            db_session=db,
            days_ago=min_feedback_days,
        )
        
        feedback_texts = feedback_data.get("training_texts", [])
        feedback_labels = feedback_data.get("training_labels", [])
        bias_analysis = feedback_data.get("bias_analysis", {})
        
        if not feedback_texts:
            return {
                "status": "warning",
                "message": f"No biased feedback found in last {min_feedback_days} days. Skipping retraining.",
                "minimum_required": 5,
                "feedback_found": 0,
            }
        
        if len(feedback_texts) < 5:
            return {
                "status": "warning",
                "message": f"Only {len(feedback_texts)} biased feedback found. Minimum 5 recommended for reliable retraining.",
                "feedback_found": len(feedback_texts),
                "bias_patterns": bias_analysis.get("patterns", {}),
            }
        
        # Step 2: Retrain model
        logger.info(f"Retraining with {len(feedback_texts)} feedback corrections...")
        result = await retrainer.retrain_with_feedback(
            feedback_texts=feedback_texts,
            feedback_labels=feedback_labels,
            mix_ratio=mix_original_ratio,
        )
        
        # Step 3: Compare with previous model
        comparison = await retrainer.compare_models()
        
        result["bias_analysis"] = bias_analysis
        result["model_comparison"] = comparison
        
        logger.warning(
            f"MODEL RETRAINING COMPLETE - "
            f"New test accuracy: {result['metrics'].get('accuracy', 'N/A'):.2%}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error during model retraining: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")


@router.get("/model-versions")
async def get_model_versions(
    retrainer: ModelRetrainer = Depends(get_model_retrainer),
):
    """
    Get history of trained model versions with performance metrics.
    
    Useful for:
    - Tracking model improvements over time
    - Comparing different feedback mix strategies
    - Reverting to previous versions if needed
    """
    try:
        import json
        from pathlib import Path
        
        versions_file = retrainer.model_dir / "versions.json"
        
        if not versions_file.exists():
            return {
                "status": "info",
                "message": "No version history available yet",
                "versions": []
            }
        
        with open(versions_file) as f:
            versions = json.load(f)
        
        # Include latest version info
        return {
            "status": "success",
            "total_versions": len(versions),
            "versions": versions,
            "latest": versions[-1] if versions else None,
        }
    except Exception as e:
        logger.error(f"Error fetching model versions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-models")
async def compare_models_endpoint(
    retrainer: ModelRetrainer = Depends(get_model_retrainer),
):
    """
    Compare current model with previous version.
    
    Shows accuracy improvement/regression and feedback impact.
    """
    try:
        comparison = await retrainer.compare_models()
        
        return {
            "status": "success",
            "comparison": comparison,
        }
    except Exception as e:
        logger.error(f"Error comparing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))
