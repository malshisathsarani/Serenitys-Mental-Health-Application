"""
Chatbot Service
Intelligent conversational AI that uses ML predictions to provide mental health support
"""
import logging
from typing import Dict, Optional
from app.services.ml_service import get_ml_service

logger = logging.getLogger(__name__)


class ChatbotService:
    """Service for generating intelligent chatbot responses based on ML predictions"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        logger.info("Initializing Chatbot Service...")
        self.ml_service = get_ml_service()
        self._initialized = True
        
        # Response templates based on mental health predictions
        self.response_templates = {
            "Anxiety": [
                "I notice you might be feeling anxious. That's completely valid. Would you like to try a breathing exercise or talk about what's on your mind?",
                "It sounds like you're experiencing some anxiety. Remember, these feelings are temporary. Would you like some coping strategies?",
                "I understand you're feeling anxious right now. Let's work through this together. What would help you most - a grounding technique or just talking?"
            ],
            "Depression": [
                "I hear that you're going through a difficult time. Your feelings are valid, and I'm here to support you. Would you like to talk about what's been weighing on you?",
                "It sounds like things have been really tough lately. Please know that you're not alone. Would you like to explore some gentle activities that might help?",
                "Thank you for sharing how you're feeling. Depression can be overwhelming, but there are ways to manage it. Would you like to talk more or learn about resources?"
            ],
            "Suicidal": [
                "⚠️ I'm very concerned about what you've shared. Please know that help is available right now. Would you like me to connect you with a crisis helpline?",
                "⚠️ Your safety is the top priority. Please reach out to a crisis helpline immediately or call emergency services. I'm here, but professional help is crucial right now.",
                "⚠️ I'm worried about you. If you're having thoughts of harming yourself, please contact a crisis helpline or go to the nearest emergency room. Would you like crisis resources?"
            ],
            "Normal": [
                "Thank you for sharing with me. How are you feeling today?",
                "I'm here to listen and support you. What would you like to talk about?",
                "That's great to hear. Is there anything specific you'd like to explore or discuss?"
            ]
        }
        
        # Crisis resources
        self.crisis_resources = {
            "hotlines": [
                "National Suicide Prevention Lifeline: 988 or 1-800-273-8255",
                "Crisis Text Line: Text HOME to 741741",
                "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
            ]
        }
    
    def generate_response(self, user_message: str, conversation_context: Optional[list] = None) -> Dict:
        """
        Generate intelligent chatbot response based on ML analysis
        
        Args:
            user_message: The user's input message
            conversation_context: Optional list of previous messages for context
            
        Returns:
            Dictionary with response, prediction, and metadata
        """
        try:
            # Get ML prediction
            prediction_result = self.ml_service.predict(user_message)
            
            if prediction_result['status'] == 'error':
                logger.error(f"ML prediction failed: {prediction_result.get('message')}")
                return {
                    "response": "I'm having trouble processing that right now. Could you try rephrasing?",
                    "prediction": None,
                    "probabilities": {},
                    "status": "error"
                }
            
            prediction = prediction_result['prediction']
            probabilities = prediction_result['probabilities']
            
            # Generate appropriate response based on prediction
            response_text = self._get_contextual_response(
                prediction, 
                probabilities,
                user_message,
                conversation_context
            )
            
            # Add crisis resources if needed
            crisis_detected = prediction == "Suicidal" or probabilities.get("Suicidal", 0) > 0.3
            
            result = {
                "response": response_text,
                "prediction": prediction,
                "probabilities": probabilities,
                "status": "success",
                "crisis_detected": crisis_detected,
                "requires_professional_help": crisis_detected or prediction in ["Suicidal", "Depression"]
            }
            
            if crisis_detected:
                result["crisis_resources"] = self.crisis_resources
            
            logger.info(f"Generated response for prediction: {prediction}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating chatbot response: {str(e)}", exc_info=True)
            return {
                "response": "I'm here to help, but I'm experiencing a technical issue. Please try again.",
                "prediction": None,
                "probabilities": {},
                "status": "error",
                "error": str(e)
            }
    
    def _get_contextual_response(
        self, 
        prediction: str, 
        probabilities: Dict[str, float],
        user_message: str,
        conversation_context: Optional[list] = None
    ) -> str:
        """
        Generate contextual response based on prediction and conversation history
        
        Args:
            prediction: ML model prediction
            probabilities: Prediction probabilities
            user_message: User's message
            conversation_context: Previous conversation messages
            
        Returns:
            Contextual response string
        """
        # Get base response from templates
        import random
        templates = self.response_templates.get(prediction, self.response_templates["Normal"])
        base_response = random.choice(templates)
        
        # Add contextual awareness
        # Check if this is a follow-up in conversation
        if conversation_context and len(conversation_context) > 2:
            # User has been talking for a while - show empathy
            empathy_prefixes = [
                "I've been listening, and ",
                "Thank you for continuing to share. ",
                "I appreciate you opening up. "
            ]
            if prediction in ["Anxiety", "Depression", "Suicidal"]:
                base_response = random.choice(empathy_prefixes) + base_response.lower()
        
        # Add confidence-based nuancing
        confidence = probabilities.get(prediction, 0)
        
        if confidence < 0.5 and prediction != "Normal":
            # Lower confidence - be more exploratory
            base_response += " I want to understand better - can you tell me more?"
        
        return base_response
    
    def get_greeting(self) -> str:
        """Get initial greeting message"""
        return "Hello! I'm here to support you. How are you feeling today?"
    
    def get_crisis_resources(self) -> Dict:
        """Get crisis support resources"""
        return self.crisis_resources


# Singleton accessor
def get_chatbot_service() -> ChatbotService:
    """Get or create chatbot service instance"""
    return ChatbotService()
