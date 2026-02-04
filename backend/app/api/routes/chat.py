"""
Chat API Routes
Endpoints for chatbot conversation
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chatbot_service import get_chatbot_service, ChatbotService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Send a message to the chatbot and receive an AI response
    
    - **message**: User's message text
    - **conversation_history**: Optional list of previous messages for context
    
    Returns chatbot response with mental health analysis
    """
    try:
        # Generate response using chatbot service
        result = chatbot_service.generate_response(
            user_message=request.message,
            conversation_context=request.conversation_history
        )
        
        if result['status'] == 'error':
            raise HTTPException(
                status_code=500, 
                detail=result.get('error', 'Failed to generate response')
            )
        
        return ChatResponse(
            response=result['response'],
            prediction=result.get('prediction'),
            probabilities=result.get('probabilities', {}),
            crisis_detected=result.get('crisis_detected', False),
            requires_professional_help=result.get('requires_professional_help', False),
            crisis_resources=result.get('crisis_resources'),
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat message error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.get("/greeting")
async def get_greeting(chatbot_service: ChatbotService = Depends(get_chatbot_service)):
    """Get initial greeting message"""
    return {
        "message": chatbot_service.get_greeting(),
        "status": "success"
    }


@router.get("/crisis-resources")
async def get_crisis_resources(chatbot_service: ChatbotService = Depends(get_chatbot_service)):
    """Get crisis support resources"""
    return {
        "resources": chatbot_service.get_crisis_resources(),
        "status": "success"
    }
