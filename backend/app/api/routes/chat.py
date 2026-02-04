"""
Chat API Routes
Endpoints for chatbot conversation with database persistence
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import logging

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chatbot_service import get_chatbot_service, ChatbotService
from app.core.database import get_db
from app.models.database import Conversation, Message, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the chatbot and receive an AI response
    Saves conversation to MySQL database
    
    - **message**: User's message text
    - **conversation_history**: Optional list of previous messages for context
    
    Returns chatbot response with mental health analysis
    """
    try:
        # Use default user for now (will be from auth later)
        user_id = 1
        conversation_id = None
        
        # Ensure user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(id=user_id, username="default_user", email="user@serenity.app")
            db.add(user)
            await db.flush()
        
        # Create new conversation for each message (simplified for now)
        conversation = Conversation(
            user_id=user_id,
            title=f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            started_at=datetime.utcnow(),
            last_message_at=datetime.utcnow()
        )
        db.add(conversation)
        await db.flush()
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        
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
        
        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result['response'],
            timestamp=datetime.utcnow(),
            prediction=result.get('prediction'),
            probabilities=result.get('probabilities'),
            crisis_detected=result.get('crisis_detected', False)
        )
        db.add(assistant_message)
        
        # Update conversation
        conversation.last_message_at = datetime.utcnow()
        conversation.message_count += 2  # User + assistant
        if result.get('crisis_detected'):
            conversation.crisis_detected = True
        
        await db.commit()
        
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
        await db.rollback()
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
