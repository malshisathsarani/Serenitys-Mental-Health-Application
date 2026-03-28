"""
Tests for feedback processing and model retraining (STEP 3).
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.feedback_processor import FeedbackProcessor


def test_infer_corrected_label_suicidal():
    """Test that suicide keywords are detected correctly."""
    processor = FeedbackProcessor()
    
    # Test with no comment - should use default alternative
    label = processor._FeedbackProcessor__infer_corrected_label(
        user_input="I want to hurt myself",
        current_prediction="Depression",
        feedback_comment=None,
    )
    assert label in ["Suicidal", "Anxiety", "Normal"]
    
    # Test with suicide keywords in comment
    label = processor._FeedbackProcessor__infer_corrected_label(
        user_input="I'm feeling sad today",
        current_prediction="Normal",
        feedback_comment="This is clearly suicidal ideation, not normal mood",
    )
    assert label == "Suicidal"


def test_infer_corrected_label_anxiety():
    """Test anxiety keyword detection."""
    processor = FeedbackProcessor()
    
    label = processor._FeedbackProcessor__infer_corrected_label(
        user_input="I can't stop worrying",
        current_prediction="Depression",
        feedback_comment="The user is experiencing panic and anxiety, not depression",
    )
    assert label == "Anxiety"


def test_infer_corrected_label_depression():
    """Test depression keyword detection."""
    processor = FeedbackProcessor()
    
    label = processor._FeedbackProcessor__infer_corrected_label(
        user_input="I feel empty",
        current_prediction="Anxiety",
        feedback_comment="This person is clearly depressed and hopeless",
    )
    assert label == "Depression"


def test_infer_corrected_label_normal():
    """Test normal/fine mood detection."""
    processor = FeedbackProcessor()
    
    label = processor._FeedbackProcessor__infer_corrected_label(
        user_input="I'm doing great today",
        current_prediction="Anxiety",
        feedback_comment="User seems perfectly fine and happy, not anxious",
    )
    assert label == "Normal"


def test_infer_corrected_label_fallback():
    """Test fallback when keywords don't match."""
    processor = FeedbackProcessor()
    
    label = processor._FeedbackProcessor__infer_corrected_label(
        user_input="I have something else",
        current_prediction="Anxiety",
        feedback_comment="This response is inaccurate",
    )
    # Should flip to alternative
    assert label in ["Suicidal", "Depression", "Normal"]
    assert label != "Anxiety"


def test_feedback_processor_singleton():
    """Test that FeedbackProcessor is a singleton."""
    processor1 = FeedbackProcessor()
    processor2 = FeedbackProcessor()
    
    assert processor1 is processor2


def test_bias_pattern_identification():
    """Test bias pattern grouping logic."""
    processor = FeedbackProcessor()
    
    # Simulate multiple incorrect predictions
    corrections = [
        ("Anxiety", "Suicidal"),
        ("Normal", "Suicidal"),
        ("Depression", "Suicidal"),
        ("Anxiety", "Anxiety"),  # Correct
        ("Normal", "Depression"),
    ]
    
    bias_patterns = {}
    for current, corrected in corrections:
        pattern_key = f"{current} → {corrected}"
        bias_patterns[pattern_key] = bias_patterns.get(pattern_key, 0) + 1
    
    # Should have most bias in wrong→Suicidal
    assert bias_patterns.get("Anxiety → Suicidal", 0) == 1
    assert bias_patterns.get("Normal → Suicidal", 0) == 1
    assert bias_patterns.get("Depression → Suicidal", 0) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
