"""
Unit Tests for Model Loading and Prediction
"""
import pytest
from pathlib import Path
import joblib
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import load_model_and_labels, get_flags, decide_action

class TestModelLoading:
    """Test model loading functionality"""
    
    def test_model_loading_succeeds(self):
        """Test that model loads without errors"""
        try:
            model, vectorizer, labels = load_model_and_labels()
            assert model is not None
        except FileNotFoundError:
            pytest.skip("Model file not found - expected in test environment")
    
    def test_model_has_predict(self):
        """Test that loaded model has predict method"""
        try:
            model, vectorizer, labels = load_model_and_labels()
            assert hasattr(model, "predict")
        except FileNotFoundError:
            pytest.skip("Model file not found")
    
    def test_vectorizer_can_transform(self):
        """Test that vectorizer can transform text"""
        try:
            model, vectorizer, labels = load_model_and_labels()
            if vectorizer is not None:
                result = vectorizer.transform(["test text"])
                assert result is not None
        except FileNotFoundError:
            pytest.skip("Model file not found")

class TestSafetyRules:
    """Test safety flag detection rules"""
    
    def test_get_flags_intent(self):
        """Test intent pattern detection"""
        text = "I will kill myself"
        flags = get_flags(text)
        assert "intent" in flags
    
    def test_get_flags_time(self):
        """Test time pattern detection"""
        text = "I want to do it tonight"
        flags = get_flags(text)
        assert "time" in flags
    
    def test_get_flags_plan(self):
        """Test plan pattern detection"""
        text = "I have a plan for this"
        flags = get_flags(text)
        assert "plan" in flags
    
    def test_get_flags_means(self):
        """Test means pattern detection"""
        text = "I have pills and a rope"
        flags = get_flags(text)
        assert "means" in flags
    
    def test_get_flags_multiple(self):
        """Test detection of multiple flags"""
        text = "I will kill myself tonight with pills"
        flags = get_flags(text)
        assert "intent" in flags
        assert "time" in flags
        assert "means" in flags
    
    def test_get_flags_none(self):
        """Test that safe text has no flags"""
        text = "I am having a great day"
        flags = get_flags(text)
        assert len(flags) == 0
    
    def test_flags_case_insensitive(self):
        """Test that flag detection is case insensitive"""
        text_upper = "I WILL KILL MYSELF"
        text_lower = "i will kill myself"
        flags_upper = get_flags(text_upper)
        flags_lower = get_flags(text_lower)
        assert flags_upper == flags_lower

class TestActionDecision:
    """Test action recommendation logic"""
    
    def test_crisis_critical_intent_and_time(self):
        """Test critical crisis when intent and time are present"""
        action = decide_action("normal", 0.8, ["intent", "time"])
        assert action == "crisis_critical"
    
    def test_crisis_critical_plan_and_intent(self):
        """Test critical crisis when plan and intent are present"""
        action = decide_action("normal", 0.8, ["plan", "intent"])
        assert action == "crisis_critical"
    
    def test_crisis_high_single_flag(self):
        """Test high crisis with any single flag"""
        action = decide_action("normal", 0.8, ["intent"])
        assert action == "crisis_high"
    
    def test_crisis_high_suicidal_label(self):
        """Test high crisis with suicidal label"""
        action = decide_action("suicidal", 0.8, [])
        assert action == "crisis_high"
    
    def test_uncertain_low_confidence(self):
        """Test uncertain action with low confidence"""
        action = decide_action("normal", 0.3, [])
        assert action == "uncertain_support"
    
    def test_normal_action(self):
        """Test normal action with good conditions"""
        action = decide_action("normal", 0.9, [])
        assert action == "normal"
    
    def test_confidence_threshold(self):
        """Test confidence threshold at 0.55"""
        action_low = decide_action("normal", 0.54, [])
        action_high = decide_action("normal", 0.56, [])
        assert action_low == "uncertain_support"
        assert action_high == "normal"
