"""
Feedback Processing Service - STEP 3 Bias Reduction
Processes user feedback to identify and correct biased model responses.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.database import Message, MessageFeedback, Conversation
from app.core.config import settings

logger = logging.getLogger(__name__)


class FeedbackProcessor:
    """Process user feedback to identify biased/problematic model responses."""

    _instance: Optional["FeedbackProcessor"] = None

    def __new__(cls):
        if cls._instance is None:
            inst = super().__new__(cls)
            inst._initialized = False
            cls._instance = inst
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        logger.info("Initializing Feedback Processor (STEP 3 - Bias Reduction)")
        self._initialized = True

    async def extract_feedback_training_data(
        self,
        db_session: AsyncSession,
        days_ago: int = 30,
        min_feedback_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Extract training data from user feedback.
        
        Process flow:
        1. Query all feedback from last N days
        2. Filter messages where unhelpful=True (biased/wrong responses)
        3. Link feedback back to original message and user input
        4. Group by prediction type to identify bias patterns
        5. Return labeled dataset for retraining
        
        Args:
            db_session: Database session
            days_ago: Only include feedback from last N days
            min_feedback_count: Minimum feedbacks to include
            
        Returns:
            Dict with:
            - training_texts: List of text inputs
            - training_labels: List of corrected labels
            - bias_analysis: Patterns identified
            - metadata: Timestamp, record count, etc.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_ago)
        
        try:
            # Query feedback + linked messages
            result = await db_session.execute(
                select(
                    MessageFeedback,
                    Message,
                    Conversation,
                )
                .join(Message, MessageFeedback.message_id == Message.id)
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(
                    and_(
                        MessageFeedback.created_at >= cutoff_date,
                        MessageFeedback.helpful == False,  # Unhelpful = biased/wrong
                    )
                )
                .order_by(MessageFeedback.created_at.desc())
            )
            
            rows = result.fetchall()
            
            if not rows:
                logger.info(f"No unhelpful feedback found in last {days_ago} days")
                return {
                    "training_texts": [],
                    "training_labels": [],
                    "bias_analysis": {},
                    "metadata": {
                        "feedback_count": 0,
                        "extracted_at": datetime.utcnow().isoformat(),
                    }
                }
            
            training_texts = []
            training_labels = []
            bias_patterns = {}  # Group by prediction type
            
            # Process feedback records
            for feedback, message, conversation in rows:
                # Get the user input (previous message in conversation)
                # Message.role = "assistant", need to find corresponding user message
                user_input = await self._get_user_input_for_message(
                    db_session, 
                    conversation.id, 
                    message.id
                )
                
                if not user_input:
                    logger.warning(f"Could not find user input for message {message.id}")
                    continue
                
                # Extract current prediction
                current_prediction = message.prediction or "Unknown"
                
                # Feedback comment might hint at correct label
                corrected_label = self._infer_corrected_label(
                    user_input=user_input,
                    current_prediction=current_prediction,
                    feedback_comment=feedback.comment,
                )
                
                training_texts.append(user_input)
                training_labels.append(corrected_label)
                
                # Track bias pattern: "prediction -> corrected_to"
                pattern_key = f"{current_prediction} → {corrected_label}"
                bias_patterns[pattern_key] = bias_patterns.get(pattern_key, 0) + 1
                
                logger.debug(
                    f"Feedback: user_input='{user_input[:50]}...' "
                    f"was_predicted={current_prediction} "
                    f"corrected_to={corrected_label}"
                )
            
            result_data = {
                "training_texts": training_texts,
                "training_labels": training_labels,
                "bias_analysis": {
                    "patterns": bias_patterns,
                    "most_common_bias": max(bias_patterns.items(), key=lambda x: x[1])[0]
                    if bias_patterns else None,
                    "total_biased_responses": len(training_texts),
                },
                "metadata": {
                    "feedback_count": len(training_texts),
                    "days_analyzed": days_ago,
                    "extracted_at": datetime.utcnow().isoformat(),
                    "cutoff_date": cutoff_date.isoformat(),
                }
            }
            
            logger.info(
                f"Extracted {len(training_texts)} biased responses for retraining. "
                f"Top bias pattern: {result_data['bias_analysis']['most_common_bias']}"
            )
            
            return result_data
            
        except Exception as e:
            logger.error(f"Error extracting feedback training data: {e}", exc_info=True)
            raise

    async def _get_user_input_for_message(
        self,
        db_session: AsyncSession,
        conversation_id: int,
        assistant_message_id: int,
    ) -> Optional[str]:
        """Find the user message that prompted this assistant response."""
        try:
            # Get all messages in conversation, ordered by timestamp
            result = await db_session.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.timestamp)
            )
            messages = result.scalars().all()
            
            # Find assistant message index
            assistant_idx = None
            for idx, msg in enumerate(messages):
                if msg.id == assistant_message_id:
                    assistant_idx = idx
                    break
            
            if assistant_idx is None or assistant_idx == 0:
                return None
            
            # Get previous message (should be user message)
            prev_message = messages[assistant_idx - 1]
            if prev_message.role == "user":
                return prev_message.content
            
            return None
        except Exception as e:
            logger.error(f"Error finding user input for message: {e}")
            return None

    def _infer_corrected_label(
        self,
        user_input: str,
        current_prediction: str,
        feedback_comment: Optional[str],
    ) -> str:
        """
        Infer corrected label from feedback comment.
        
        Heuristics:
        - If comment mentions "crisis" or "suicide" → label as "Suicidal"
        - If comment mentions anxiety/panic → "Anxiety"
        - If comment mentions sadness/hopeless → "Depression"
        - Otherwise, use inverse of current prediction (toggle incorrectness)
        """
        if not feedback_comment:
            # Default: if current was wrong, just flip to most common alternative
            alternatives = {"Suicidal": "Depression", "Depression": "Anxiety", "Anxiety": "Normal", "Normal": "Anxiety"}
            return alternatives.get(current_prediction, "Depression")
        
        comment_lower = feedback_comment.lower()
        
        # Pattern matching for corrected label
        if any(word in comment_lower for word in ["suicidal", "suicide", "kill myself", "die", "harm", "crisis"]):
            return "Suicidal"
        elif any(word in comment_lower for word in ["anxiety", "panic", "worry", "nervous", "afraid"]):
            return "Anxiety"
        elif any(word in comment_lower for word in ["depression", "depressed", "sad", "hopeless", "empty", "worthless"]):
            return "Depression"
        elif any(word in comment_lower for word in ["normal", "fine", "okay", "good", "happy"]):
            return "Normal"
        
        # Default fallback
        alternatives = {"Suicidal": "Depression", "Depression": "Anxiety", "Anxiety": "Normal", "Normal": "Anxiety"}
        return alternatives.get(current_prediction, "Depression")

    async def calculate_bias_metrics(
        self,
        db_session: AsyncSession,
        prediction_category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate fairness metrics to detect bias patterns.
        
        Metrics calculated:
        - Helpful rate by prediction type (e.g., "Suicidal" has 60% helpful)
        - False positive/negative rates
        - Confidence-sorted metrics for top predictions
        
        Args:
            db_session: Database session
            prediction_category: Optional filter (e.g., "Suicidal")
            
        Returns:
            Dict with bias metrics and interpretation
        """
        try:
            # Query all feedback with message predictions
            result = await db_session.execute(
                select(MessageFeedback, Message)
                .join(Message, MessageFeedback.message_id == Message.id)
            )
            rows = result.fetchall()
            
            if not rows:
                logger.info("No feedback data available for bias metrics")
                return {"error": "No feedback data", "recommendation": "Collect more feedback"}
            
            # Group by prediction type
            metrics_by_prediction = {}
            
            for feedback, message in rows:
                pred = message.prediction or "Unknown"
                if prediction_category and pred != prediction_category:
                    continue
                
                if pred not in metrics_by_prediction:
                    metrics_by_prediction[pred] = {
                        "total": 0,
                        "helpful": 0,
                        "unhelpful": 0,
                        "confidence_avg": 0.0,
                        "messages": []
                    }
                
                metrics_by_prediction[pred]["total"] += 1
                if feedback.helpful:
                    metrics_by_prediction[pred]["helpful"] += 1
                else:
                    metrics_by_prediction[pred]["unhelpful"] += 1
                
                # Track confidence
                probs = message.probabilities or {}
                pred_prob = probs.get(pred, 0.0)
                metrics_by_prediction[pred]["messages"].append(pred_prob)
            
            # Calculate rates
            for pred, data in metrics_by_prediction.items():
                data["helpful_rate"] = (
                    data["helpful"] / data["total"] if data["total"] > 0 else 0.0
                )
                data["confidence_avg"] = (
                    sum(data["messages"]) / len(data["messages"]) 
                    if data["messages"] else 0.0
                )
                data.pop("messages", None)  # Remove raw messages
            
            # Identify concerning categories
            concerning = {
                pred: data for pred, data in metrics_by_prediction.items()
                if data["helpful_rate"] < 0.6 and data["total"] >= 5
            }
            
            return {
                "metrics_by_prediction": metrics_by_prediction,
                "concerning_categories": concerning,
                "recommendation": (
                    f"Categories with <60% helpful rate and ≥5 feedback: {list(concerning.keys())}"
                    if concerning else "Model appears fair - no concerning biases detected"
                ),
                "calculated_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error calculating bias metrics: {e}", exc_info=True)
            raise


def get_feedback_processor() -> FeedbackProcessor:
    """FastAPI dependency provider."""
    return FeedbackProcessor()
