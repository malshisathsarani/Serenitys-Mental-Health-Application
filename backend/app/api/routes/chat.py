"""
Chat API Routes
Endpoints for chatbot conversation with database persistence
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional
import logging

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chatbot_service import get_chatbot_service, ChatbotService
from app.services.crisis_fusion_service import (
    get_crisis_fusion_service,
    CrisisFusionService,
)
from app.services.emergency_service import (
    get_emergency_service,
    EmergencyService,
)
from app.core.database import get_db
from app.models.database import Conversation, Message, User, EmergencyContact

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
    fusion_service: CrisisFusionService = Depends(get_crisis_fusion_service),
    emergency_service: EmergencyService = Depends(get_emergency_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the chatbot and receive an AI response
    Saves conversation to MySQL database.
    Automatically triggers emergency response if crisis detected.

    - **message**: User's message text
    - **conversation_history**: Optional list of previous messages for context
    - **conversation_id**: Optional id to continue an existing conversation
    - **voice_risk_score**: Optional voice risk score from audio analysis
    - **voice_crisis_detected**: Optional voice crisis flag

    Returns chatbot response with mental health analysis.
    Triggers automatic emergency calling if high-risk crisis detected.
    """
    try:
        # Use default user for now (will be from auth later)
        user_id = 1

        # Ensure user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(id=user_id, username="default_user", email="user@serenity.app")
            db.add(user)
            await db.flush()

        conversation: Optional[Conversation] = None
        if request.conversation_id is not None:
            conv_result = await db.execute(
                select(Conversation).where(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == user_id,
                )
            )
            conversation = conv_result.scalar_one_or_none()
            if conversation is None:
                logger.warning(
                    "conversation_id=%s not found for user_id=%s; starting new conversation",
                    request.conversation_id,
                    user_id,
                )

        if conversation is None:
            conversation = Conversation(
                user_id=user_id,
                title=f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                started_at=datetime.utcnow(),
                last_message_at=datetime.utcnow(),
            )
            db.add(conversation)
            await db.flush()

        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            timestamp=datetime.utcnow(),
        )
        db.add(user_message)

        # Generate response using chatbot service
        result = chatbot_service.generate_response(
            user_message=request.message,
            conversation_context=request.conversation_history,
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate response"),
            )

        # Fuse multimodal signals
        fused = fusion_service.fuse(
            text_crisis_detected=bool(result.get("crisis_detected", False)),
            prediction=result.get("prediction"),
            probabilities=result.get("probabilities") or {},
            voice_crisis_detected=request.voice_crisis_detected,
            voice_risk_score=request.voice_risk_score,
        )
        crisis_detected = bool(fused["crisis_detected"])
        crisis_fusion_sources = list(fused["sources"])

        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["response"],
            timestamp=datetime.utcnow(),
            prediction=result.get("prediction"),
            probabilities=result.get("probabilities"),
            crisis_detected=crisis_detected,
        )
        db.add(assistant_message)

        # Update conversation
        conversation.last_message_at = datetime.utcnow()
        conversation.message_count += 2  # User + assistant
        if crisis_detected:
            conversation.crisis_detected = True

        await db.flush()

        # STEP 2: TRIGGER EMERGENCY CALLING IF CRISIS DETECTED
        emergency_call_result = None
        if crisis_detected:
            # Check if emergency call should be triggered
            should_call = await emergency_service.should_trigger_emergency_call(
                fused_risk_score=fused.get("fused_risk_score"),
                text_risk_score=fused.get("text_risk_score", 0.0),
                voice_risk_score=fused.get("voice_risk_score"),
                crisis_detected=crisis_detected,
                prediction=result.get("prediction", "Unknown"),
            )
            
            if should_call:
                # Get user's emergency contacts
                contact_result = await db.execute(
                    select(EmergencyContact).where(
                        EmergencyContact.user_id == user_id,
                        EmergencyContact.is_active == True
                    )
                )
                emergency_contacts = contact_result.scalars().all()
                
                # Trigger emergency calling
                logger.critical(f"CRISIS DETECTED FOR USER {user_id} - TRIGGERING EMERGENCY CALLS")
                emergency_call_result = await emergency_service.trigger_emergency_call(
                    user_id=user_id,
                    conversation_id=conversation.id,
                    message_id=assistant_message.id,
                    fused_risk_score=fused.get("fused_risk_score"),
                    text_risk_score=fused.get("text_risk_score", 0.0),
                    voice_risk_score=fused.get("voice_risk_score"),
                    prediction=result.get("prediction", "Unknown"),
                    emergency_contacts=emergency_contacts if emergency_contacts else None,
                    db_session=db,
                )
                
                logger.warning(f"Emergency call result: {emergency_call_result}")

        await db.commit()

        response = ChatResponse(
            response=result["response"],
            conversation_id=conversation.id,
            assistant_message_id=assistant_message.id,
            prediction=result.get("prediction"),
            probabilities=result.get("probabilities", {}),
            crisis_detected=crisis_detected,
            crisis_fusion_sources=crisis_fusion_sources,
            fused_risk_score=fused.get("fused_risk_score"),
            voice_risk_score=fused.get("voice_risk_score"),
            requires_professional_help=result.get("requires_professional_help", False),
            crisis_resources=result.get("crisis_resources"),
            status="success",
        )

        return response

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
        "status": "success",
    }


@router.post("", response_model=ChatResponse)
async def send_message_root(
    request: ChatRequest,
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
    fusion_service: CrisisFusionService = Depends(get_crisis_fusion_service),
    emergency_service: EmergencyService = Depends(get_emergency_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Convenience endpoint: POST /api/chat
    Same as POST /api/chat/message - sends message and gets response
    """
    return await send_message(
        request=request,
        chatbot_service=chatbot_service,
        fusion_service=fusion_service,
        emergency_service=emergency_service,
        db=db,
    )


@router.get("/crisis-resources")
async def get_crisis_resources(
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
):
    """Get crisis support resources"""
    return {
        "resources": chatbot_service.get_crisis_resources(),
        "status": "success",
    }
