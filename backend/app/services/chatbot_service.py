"""
Chatbot Service
Hybrid Intelligent conversational AI combining ML predictions with NLP keyword detection
for personalized mental health support responses
"""
import logging
import re
import random
from typing import Dict, Optional, Tuple
from app.services.ml_service import get_ml_service

logger = logging.getLogger(__name__)


class ChatbotService:
    """Service for generating intelligent chatbot responses using hybrid NLP+ML approach"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        logger.info("Initializing Chatbot Service (Hybrid NLP+ML)...")
        self.ml_service = get_ml_service()
        self._initialized = True
        
        # Keyword dictionaries for NLP-based topic detection
        self.keywords = {
            "anxiety": {
                "worried", "anxious", "nervous", "uneasy", "stressed", "panic", "afraid",
                "overwhelmed", "tense", "apprehensive", "jittery", "restless", "tension",
                "scary", "frightened", "dread", "doom"
            },
            "depression": {
                "sad", "depressed", "hopeless", "worthless", "empty", "lost", "numb",
                "down", "low", "miserable", "unhappy", "gloomy", "despair", "blue",
                "tired", "exhausted", "unmotivated"
            },
            "suicidal": {
                "kill myself", "end it", "suicide", "harm myself", "hurt myself",
                "no point", "better off dead", "want to die", "not worth living",
                "disappear", "check out", "give up"
            },
            "positive": {
                "happy", "glad", "joyful", "great", "wonderful", "fantastic", "excellent",
                "good", "better", "improving", "hopeful", "positive", "proud", "accomplished"
            },
            "sleep": {
                "sleep", "insomnia", "tired", "exhausted", "fatigue", "nightmare",
                "restless", "can't sleep", "awake", "insomniac", "sleepless", "doze"
            },
            "work": {
                "work", "job", "boss", "coworker", "deadline", "project", "meeting",
                "office", "career", "employment", "fired", "quit", "stress at work",
                "workplace", "promotion"
            },
            "relationship": {
                "relationship", "partner", "boyfriend", "girlfriend", "spouse", "husband",
                "wife", "dating", "breakup", "divorce", "marriage", "love", "family",
                "friend", "lonely", "alone", "conflict"
            },
            "health": {
                "pain", "sick", "illness", "disease", "health", "medical", "doctor",
                "hospital", "symptom", "injury", "accident", "disabled", "chronic"
            },
            "substance": {
                "drink", "alcohol", "drugs", "junkie", "addict", "high", "drunk",
                "smoking", "cocaine", "heroin", "pills", "substance", "dependence"
            }
        }
        
        # Response templates with {topic} placeholder for personalization
        self.response_templates = {
            "Anxiety": [
                "I hear your anxiety about {topic}. That's completely valid. Would you like to try a breathing exercise or talk more?",
                "It sounds like you're feeling anxious about {topic}. Remember, these feelings are temporary. Would you like some coping strategies?",
                "I understand you're anxious about {topic} right now. Let's work through this together. What would help you most?",
                "Anxiety about {topic} is challenging, but you're not alone. Would you like to explore what's specifically worrying you?"
            ],
            "Depression": [
                "I hear that {topic} is weighing on you. Your feelings are valid, and I'm here to support you. Would you like to talk more?",
                "It sounds like {topic} has been really tough lately. Please know you're not alone. Would you like to explore some ways to help?",
                "Thank you for sharing about {topic}. These feelings are real, but there are ways to manage them. Would you like to talk more?",
                "I sense depression around {topic}. That's difficult, but recovery is possible. What support would help you most right now?"
            ],
            "Suicidal": [
                "⚠️ I'm very concerned about {topic}. Your safety is the priority. Please reach out to crisis support now: 988 or Crisis Text Line (text HOME to 741741).",
                "⚠️ I hear thoughts of {topic}. This is critical. Please contact emergency services or the National Suicide Prevention Lifeline: 988.",
                "⚠️ I'm worried about {topic}. Please get immediate help: 988 (Suicide Lifeline) or go to your nearest emergency room.",
                "⚠️ {topic} is a crisis. Professional help is crucial right now. Crisis resources: 988, Crisis Text Line: Text HOME to 741741"
            ],
            "Normal": [
                "Thank you for sharing about {topic}. How are you feeling about this overall?",
                "I appreciate you telling me about {topic}. Is there anything specific you'd like to explore?",
                "That's good that you're reflecting on {topic}. What would be most helpful to discuss?"
            ]
        }
        
        # Crisis resources
        self.crisis_resources = {
            "hotlines": [
                "National Suicide Prevention Lifeline: 988 or 1-800-273-8255",
                "Crisis Text Line: Text HOME to 741741",
                "NAMI Helpline: 1-800-950-NAMI (6264) - free peer support",
                "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
            ]
        }
    
    def generate_response(self, user_message: str, conversation_context: Optional[list] = None) -> Dict:
        """
        Generate intelligent chatbot response using hybrid NLP+ML approach
        
        Args:
            user_message: The user's input message
            conversation_context: Optional list of previous messages for context
            
        Returns:
            Dictionary with response, prediction, and metadata
        """
        try:
            # Get ML prediction (core classifier)
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
            
            # NLP-based analysis: extract keywords and specific topic
            detected_keywords = self._extract_keywords(user_message)
            specific_topic = self._extract_specific_topic(user_message, detected_keywords)
            
            logger.debug(f"Detected keywords: {detected_keywords}, Topic: {specific_topic}")
            
            # Generate hybrid response combining ML + NLP
            response_text = self._get_hybrid_response(
                prediction,
                probabilities,
                user_message,
                detected_keywords,
                specific_topic,
                conversation_context
            )
            
            # Detect crisis
            crisis_detected = prediction == "Suicidal" or probabilities.get("Suicidal", 0) > 0.3
            
            result = {
                "response": response_text,
                "prediction": prediction,
                "probabilities": probabilities,
                "detected_topics": detected_keywords,
                "extracted_topic": specific_topic,
                "status": "success",
                "crisis_detected": crisis_detected,
                "requires_professional_help": crisis_detected or prediction in ["Suicidal", "Depression"]
            }
            
            if crisis_detected:
                result["crisis_resources"] = self.crisis_resources
            
            logger.info(f"Generated response for prediction: {prediction}, topics: {detected_keywords}")
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
    
    def _extract_keywords(self, user_message: str) -> list:
        """
        Extract relevant mental health keywords from user message
        
        Args:
            user_message: The user's input message
            
        Returns:
            List of detected keyword categories
        """
        message_lower = user_message.lower()
        detected = []
        
        for category, keywords in self.keywords.items():
            # Check for keyword matches using word boundaries
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', message_lower):
                    detected.append(category)
                    break  # Move to next category after first match
        
        return detected if detected else ["neutral"]
    
    def _extract_specific_topic(self, user_message: str, detected_keywords: list) -> str:
        """
        Extract specific topic/concern from user message using heuristic patterns
        
        Args:
            user_message: The user's input message
            detected_keywords: List of detected keyword categories
            
        Returns:
            Extracted specific topic or generic placeholder
        """
        # Pattern-based extraction for specific concerns
        patterns = {
            r"(about|with|regarding|concerns? about)\s+(.+?)(?:\.|$|,|\?)",
            r"I\'?m\s+(?:really\s+)?(?:very\s+)?(anxious|worried|concerned|scared)\s+(?:about|that)\s+(.+?)(?:\.|$|,|\?)",
            r"(?:my|the)\s+(.+?)\s+(?:is|is making me|makes me)\s+",
            r"(?:having|having a hard time with|struggling with)\s+(.+?)(?:\.|$|,|\?)"
        }
        
        for pattern in patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                # Return the captured group that looks like a topic (usually the last one)
                groups = match.groups()
                topic = groups[-1].strip() if groups else None
                if topic and len(topic) > 2:
                    return topic.lower()
        
        # If specific pattern not found, extract first few words if enough content
        words = user_message.split()
        if len(words) > 3:
            # Try to get meaningful topic from first few words
            topic_phrase = ' '.join(words[:4])
            return topic_phrase.lower()
        
        # Fallback: use detected category
        return detected_keywords[0] if detected_keywords else "this issue"
    
    def _get_hybrid_response(
        self,
        prediction: str,
        probabilities: Dict[str, float],
        user_message: str,
        detected_keywords: list,
        specific_topic: str,
        conversation_context: Optional[list] = None
    ) -> str:
        """
        Generate response combining ML prediction with NLP-extracted topics for personalization
        
        Args:
            prediction: ML model prediction (Anxiety/Depression/Suicidal/Normal)
            probabilities: Prediction probabilities from ML model
            user_message: Original user message
            detected_keywords: NLP-detected keyword categories
            specific_topic: NLP-extracted specific topic/concern
            conversation_context: Previous conversation messages
            
        Returns:
            Personalized response string
        """
        # Select template based on ML prediction
        templates = self.response_templates.get(prediction, self.response_templates["Normal"])
        base_response = random.choice(templates)
        
        # Personalize with extracted topic
        try:
            response_text = base_response.format(topic=specific_topic)
        except KeyError:
            # Template doesn't have {topic} placeholder - use as-is
            response_text = base_response
        
        # Add empathy based on conversation length
        if conversation_context and len(conversation_context) > 2:
            if prediction in ["Anxiety", "Depression", "Suicidal"]:
                empathy_prefixes = [
                    "I've been listening, and ",
                    "Thank you for continuing to open up. ",
                    "I appreciate your trust. "
                ]
                response_text = random.choice(empathy_prefixes) + response_text
        
        # Add exploratory follow-up if confidence is low
        confidence = probabilities.get(prediction, 0)
        if confidence < 0.5 and prediction != "Normal":
            response_text += " I want to understand better - can you tell me more about what you're experiencing?"
        
        return response_text
    
    def get_greeting(self) -> str:
        """Get initial greeting message"""
        return "Hello! I'm here to support you on your mental health journey. How are you feeling today?"
    
    def get_crisis_resources(self) -> Dict:
        """Get crisis support resources"""
        return self.crisis_resources


# Singleton accessor
def get_chatbot_service() -> ChatbotService:
    """Get or create chatbot service instance"""
    return ChatbotService()
