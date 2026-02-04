"""
Test script to verify backend-frontend integration
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n1. Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_ml_predict():
    """Test ML prediction endpoint"""
    print("\n2. Testing ML Prediction...")
    data = {
        "text": "I feel really anxious and worried about everything lately"
    }
    response = requests.post(f"{BASE_URL}/api/ml/predict", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_chat_message():
    """Test chatbot endpoint"""
    print("\n3. Testing Chat Message Endpoint...")
    data = {
        "message": "I feel really anxious and worried about everything"
    }
    response = requests.post(f"{BASE_URL}/api/chat/message", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_chat_greeting():
    """Test greeting endpoint"""
    print("\n4. Testing Greeting Endpoint...")
    response = requests.get(f"{BASE_URL}/api/chat/greeting")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_crisis_detection():
    """Test crisis detection"""
    print("\n5. Testing Crisis Detection...")
    data = {
        "message": "I don't want to live anymore, everything is hopeless"
    }
    response = requests.post(f"{BASE_URL}/api/chat/message", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    print(f"Crisis Detected: {result.get('crisis_detected')}")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("BACKEND API INTEGRATION TEST")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("ML Prediction", test_ml_predict),
        ("Chat Message", test_chat_message),
        ("Greeting", test_chat_greeting),
        ("Crisis Detection", test_crisis_detection)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, "PASSED" if passed else "FAILED"))
        except Exception as e:
            print(f"ERROR: {e}")
            results.append((name, "ERROR"))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    for name, result in results:
        status = "✅" if result == "PASSED" else "❌"
        print(f"{status} {name}: {result}")
    
    all_passed = all(r[1] == "PASSED" for r in results)
    print("\n" + ("=" * 60))
    if all_passed:
        print("✅ ALL TESTS PASSED - Integration Complete!")
    else:
        print("❌ Some tests failed - Check errors above")
    print("=" * 60)
