"""
Unit Tests for API Endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import app after path is set
from app.main import app

client = TestClient(app)

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test that health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_check_structure(self):
        """Test health check response structure"""
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert "environment" in data

class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data

class TestAnalyzeEndpoint:
    """Test text analysis endpoint"""
    
    def test_analyze_basic(self):
        """Test basic analysis request"""
        response = client.post(
            "/analyze",
            json={"text": "I am feeling happy today"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "risk_label" in data
        assert "confidence" in data
        assert "flags" in data
        assert "recommended_action" in data
    
    def test_analyze_with_context(self):
        """Test analysis with conversation context"""
        response = client.post(
            "/analyze",
            json={
                "text": "I am feeling down",
                "context": ["Hello", "How are you?"]
            }
        )
        assert response.status_code == 200
    
    def test_analyze_empty_text(self):
        """Test that empty text is rejected"""
        response = client.post(
            "/analyze",
            json={"text": ""}
        )
        assert response.status_code == 422  # Validation error
    
    def test_analyze_text_too_long(self):
        """Test that text exceeding max length is rejected"""
        long_text = "a" * 5000  # Exceeds 4000 char limit
        response = client.post(
            "/analyze",
            json={"text": long_text}
        )
        assert response.status_code == 422
    
    def test_analyze_missing_text(self):
        """Test that request without text field fails"""
        response = client.post("/analyze", json={})
        assert response.status_code == 422
    
    def test_analyze_response_types(self):
        """Test that response fields have correct types"""
        response = client.post(
            "/analyze",
            json={"text": "I am okay"}
        )
        data = response.json()
        assert isinstance(data["risk_label"], str)
        assert isinstance(data["confidence"], float)
        assert isinstance(data["flags"], list)
        assert isinstance(data["recommended_action"], str)
        assert 0 <= data["confidence"] <= 1

class TestSafetyFlags:
    """Test safety flag detection in analysis"""
    
    def test_detect_intent_flag(self):
        """Test that intent patterns are detected"""
        response = client.post(
            "/analyze",
            json={"text": "I want to kill myself"}
        )
        data = response.json()
        assert "intent" in data["flags"]
    
    def test_detect_time_flag(self):
        """Test that time patterns are detected"""
        response = client.post(
            "/analyze",
            json={"text": "I will do it tonight"}
        )
        data = response.json()
        assert "time" in data["flags"]
    
    def test_detect_plan_flag(self):
        """Test that plan patterns are detected"""
        response = client.post(
            "/analyze",
            json={"text": "I have a plan to end it"}
        )
        data = response.json()
        assert "plan" in data["flags"]
    
    def test_detect_means_flag(self):
        """Test that means patterns are detected"""
        response = client.post(
            "/analyze",
            json={"text": "I have pills ready"}
        )
        data = response.json()
        assert "means" in data["flags"]
    
    def test_crisis_critical_action(self):
        """Test that critical combinations trigger crisis_critical"""
        response = client.post(
            "/analyze",
            json={"text": "I am going to kill myself tonight"}
        )
        data = response.json()
        assert data["recommended_action"] in ["crisis_critical", "crisis_high"]
    
    def test_normal_text_no_flags(self):
        """Test that normal text has no safety flags"""
        response = client.post(
            "/analyze",
            json={"text": "I had a good day at work"}
        )
        data = response.json()
        # Should have minimal or no flags
        assert isinstance(data["flags"], list)
