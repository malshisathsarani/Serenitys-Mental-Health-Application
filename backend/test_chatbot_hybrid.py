#!/usr/bin/env python
"""Test script for hybrid chatbot implementation"""
import sys
from app.services.chatbot_service import get_chatbot_service

def test_chatbot():
    try:
        cs = get_chatbot_service()
        print("✓ Chatbot Service Loaded Successfully")
        print(f"  - Keywords: {len(cs.keywords)} categories")
        print(f"  - Response Templates: {len(cs.response_templates)} types")
        
        # Test 1: Anxiety message with specific topic
        print("\n" + "="*70)
        print("TEST 1: Anxiety Message with Specific Topic")
        print("="*70)
        resp = cs.generate_response('I am very anxious about my exam tomorrow')
        print(f"Input: 'I am very anxious about my exam tomorrow'")
        print(f"Detected Topics: {resp.get('detected_topics', [])}")
        print(f"Extracted Topic: {resp.get('extracted_topic', 'N/A')}")
        print(f"ML Prediction: {resp.get('prediction')}")
        print(f"Confidence: {resp.get('probabilities', {}).get(resp.get('prediction'), 0):.2%}")
        print(f"\nResponse:\n{resp['response']}")
        
        # Test 2: Depression with work topic
        print("\n" + "="*70)
        print("TEST 2: Depression Message with Work Topic")
        print("="*70)
        resp2 = cs.generate_response('I feel hopeless about my job; the boss is terrible and I cannot stand working there')
        print(f"Input: 'I feel hopeless about my job...'")
        print(f"Detected Topics: {resp2.get('detected_topics', [])}")
        print(f"Extracted Topic: {resp2.get('extracted_topic', 'N/A')}")
        print(f"ML Prediction: {resp2.get('prediction')}")
        print(f"\nResponse:\n{resp2['response']}")
        
        # Test 3: Normal greeting (no specific concerns)
        print("\n" + "="*70)
        print("TEST 3: Normal Greeting")
        print("="*70)
        resp3 = cs.generate_response('Hi, how are you?')
        print(f"Input: 'Hi, how are you?'")
        print(f"Detected Topics: {resp3.get('detected_topics', [])}")
        print(f"ML Prediction: {resp3.get('prediction')}")
        print(f"\nResponse:\n{resp3['response']}")
        
        # Test 4: Crisis/Suicidal ideation
        print("\n" + "="*70)
        print("TEST 4: Crisis Detection")
        print("="*70)
        resp4 = cs.generate_response('I want to kill myself and end this suffering')
        print(f"Input: 'I want to kill myself and end this suffering'")
        print(f"Detected Topics: {resp4.get('detected_topics', [])}")
        print(f"ML Prediction: {resp4.get('prediction')}")
        print(f"Crisis Detected: {resp4.get('crisis_detected')}")
        if resp4.get('crisis_resources'):
            print(f"Crisis Resources: {resp4.get('crisis_resources', {}).get('hotlines', [])}")
        print(f"\nResponse:\n{resp4['response']}")
        
        print("\n" + "="*70)
        print("✓ All Tests Completed Successfully")
        print("="*70)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(test_chatbot())
