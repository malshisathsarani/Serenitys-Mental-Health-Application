"""
Conversation Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.database import Conversation, Message, User
from app.models.schemas import ConversationResponse, ConversationDetail, MessageResponse

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: int = 1,  # Default user for now (will be from auth later)
    db: AsyncSession = Depends(get_db)
):
    """
    Get all conversations for a user
    """
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.last_message_at))
    )
    conversations = result.scalars().all()
    
    return [
        ConversationResponse(
            id=conv.id,
            title=conv.title,
            started_at=conv.started_at,
            last_message_at=conv.last_message_at,
            message_count=conv.message_count,
            is_active=conv.is_active,
            crisis_detected=conv.crisis_detected
        )
        for conv in conversations
    ]


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation details with messages
    """
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp)
    )
    messages = msg_result.scalars().all()
    
    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        started_at=conversation.started_at,
        last_message_at=conversation.last_message_at,
        message_count=conversation.message_count,
        is_active=conversation.is_active,
        crisis_detected=conversation.crisis_detected,
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                prediction=msg.prediction,
                probabilities=msg.probabilities,
                crisis_detected=msg.crisis_detected
            )
            for msg in messages
        ]
    )


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    user_id: int = 1,  # Default user for now
    title: str = "New Conversation",
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new conversation
    """
    # Ensure user exists
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        # Create default user if doesn't exist
        user = User(id=user_id, username="default_user", email="user@serenity.app")
        db.add(user)
        await db.flush()
    
    conversation = Conversation(
        user_id=user_id,
        title=title,
        started_at=datetime.utcnow(),
        last_message_at=datetime.utcnow()
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        started_at=conversation.started_at,
        last_message_at=conversation.last_message_at,
        message_count=conversation.message_count,
        is_active=conversation.is_active,
        crisis_detected=conversation.crisis_detected
    )


@router.patch("/{conversation_id}")
async def update_conversation(
    conversation_id: int,
    title: str = None,
    is_active: bool = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update conversation details
    """
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if title is not None:
        conversation.title = title
    if is_active is not None:
        conversation.is_active = is_active
    
    await db.commit()
    
    return {"message": "Conversation updated successfully"}


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation and all its messages
    """
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "Conversation deleted successfully"}
