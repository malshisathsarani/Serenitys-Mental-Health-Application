"""
Feedback API routes for response quality/bias signals.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.database import Message, MessageFeedback
from app.models.schemas import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Save user feedback for an assistant message.
    Current implementation uses default user_id=1 until auth is integrated.
    """
    user_id = 1

    message_result = await db.execute(select(Message).where(Message.id == request.message_id))
    message = message_result.scalar_one_or_none()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.role != "assistant":
        raise HTTPException(status_code=400, detail="Feedback can only target assistant messages")

    feedback = MessageFeedback(
        message_id=request.message_id,
        user_id=user_id,
        helpful=request.helpful,
        comment=request.comment.strip() if request.comment else None,
    )
    db.add(feedback)
    await db.flush()

    return FeedbackResponse(
        feedback_id=feedback.id,
        message_id=feedback.message_id,
        helpful=feedback.helpful,
        status="success",
    )

