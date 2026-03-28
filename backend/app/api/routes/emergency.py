"""
Emergency API Routes
Endpoints for emergency contact management and crisis response
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.database import EmergencyContact, EmergencyCall, User
from app.models.schemas import (
    EmergencyContactRequest,
    EmergencyContactResponse,
    EmergencyCallResponse,
    EmergencyCallListResponse,
)
from app.services.emergency_service import get_emergency_service, EmergencyService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/emergency", tags=["Emergency"])


@router.post("/contacts", response_model=EmergencyContactResponse)
async def add_emergency_contact(
    request: EmergencyContactRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Add an emergency contact for the user.
    These are people who will be called when a crisis is detected.
    
    - **name**: Contact name or relationship (e.g., "Mom", "Therapist")
    - **phone_number**: Phone number in E.164 format (e.g., +12025551234)
    - **relationship**: Description of relationship (optional)
    - **is_hotline**: Whether this is a crisis hotline
    """
    user_id = 1  # Default user (will be from auth later)
    
    try:
        # Validate user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(id=user_id, username="default_user", email="user@serenity.app")
            db.add(user)
            await db.flush()
        
        # Create emergency contact
        contact = EmergencyContact(
            user_id=user_id,
            name=request.name,
            phone_number=request.phone_number,
            contact_relationship=request.contact_relationship,
            is_hotline=request.is_hotline or False,
            is_active=True,
        )
        db.add(contact)
        await db.flush()
        
        logger.info(f"Emergency contact added for user {user_id}: {contact.name}")
        
        return EmergencyContactResponse(
            id=contact.id,
            name=contact.name,
            phone_number=contact.phone_number,
            contact_relationship=contact.contact_relationship,
            is_hotline=contact.is_hotline,
            is_active=contact.is_active,
            status="success",
        )
    
    except Exception as e:
        logger.error(f"Error adding emergency contact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contacts", response_model=List[EmergencyContactResponse])
async def get_emergency_contacts(
    db: AsyncSession = Depends(get_db),
):
    """Get all emergency contacts for the user"""
    user_id = 1  # Default user
    
    try:
        result = await db.execute(
            select(EmergencyContact)
            .where(EmergencyContact.user_id == user_id, EmergencyContact.is_active == True)
        )
        contacts = result.scalars().all()
        
        return [
            EmergencyContactResponse(
                id=c.id,
                name=c.name,
                phone_number=c.phone_number,
                contact_relationship=c.contact_relationship,
                is_hotline=c.is_hotline,
                is_active=c.is_active,
                status="success",
            )
            for c in contacts
        ]
    
    except Exception as e:
        logger.error(f"Error fetching emergency contacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/contacts/{contact_id}", response_model=EmergencyContactResponse)
async def update_emergency_contact(
    contact_id: int,
    request: EmergencyContactRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update an emergency contact"""
    user_id = 1  # Default user
    
    try:
        result = await db.execute(
            select(EmergencyContact).where(
                EmergencyContact.id == contact_id,
                EmergencyContact.user_id == user_id
            )
        )
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        contact.name = request.name
        contact.phone_number = request.phone_number
        contact.contact_relationship = request.contact_relationship
        contact.is_hotline = request.is_hotline or False
        contact.updated_at = datetime.utcnow()
        
        await db.flush()
        
        return EmergencyContactResponse(
            id=contact.id,
            name=contact.name,
            phone_number=contact.phone_number,
            contact_relationship=contact.contact_relationship,
            is_hotline=contact.is_hotline,
            is_active=contact.is_active,
            status="success",
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating emergency contact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/contacts/{contact_id}")
async def delete_emergency_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete (deactivate) an emergency contact"""
    user_id = 1  # Default user
    
    try:
        result = await db.execute(
            select(EmergencyContact).where(
                EmergencyContact.id == contact_id,
                EmergencyContact.user_id == user_id
            )
        )
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        contact.is_active = False
        contact.updated_at = datetime.utcnow()
        await db.flush()
        
        return {"status": "success", "message": "Contact deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting emergency contact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls", response_model=EmergencyCallListResponse)
async def get_emergency_calls(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get recent emergency calls made for the user (audit trail)"""
    user_id = 1  # Default user
    
    try:
        result = await db.execute(
            select(EmergencyCall)
            .where(EmergencyCall.user_id == user_id)
            .order_by(EmergencyCall.created_at.desc())
            .limit(limit)
        )
        calls = result.scalars().all()
        
        return EmergencyCallListResponse(
            total_calls=len(calls),
            calls=[
                EmergencyCallResponse(
                    id=c.id,
                    phone_number=c.phone_number,
                    call_sid=c.call_sid,
                    status=c.status,
                    crisis_type=c.crisis_type,
                    fused_risk_score=c.fused_risk_score,
                    created_at=c.created_at,
                )
                for c in calls
            ],
            status="success",
        )
    
    except Exception as e:
        logger.error(f"Error fetching emergency calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-call")
async def test_emergency_call(
    db: AsyncSession = Depends(get_db),
    emergency_service: EmergencyService = Depends(get_emergency_service),
):
    """
    Test emergency calling system (DEMO MODE).
    Simulates a crisis-level event to verify emergency calling works.
    """
    user_id = 1  # Default user
    
    try:
        # Get user's emergency contacts
        result = await db.execute(
            select(EmergencyContact).where(
                EmergencyContact.user_id == user_id,
                EmergencyContact.is_active == True
            )
        )
        contacts = result.scalars().all()
        
        # Simulate maximum risk scenario
        call_result = await emergency_service.trigger_emergency_call(
            user_id=user_id,
            conversation_id=0,  # Test conversation
            message_id=None,
            fused_risk_score=0.95,
            text_risk_score=1.0,
            voice_risk_score=0.90,
            prediction="Suicidal",
            emergency_contacts=contacts if contacts else None,
            db_session=db,
        )
        
        logger.info(f"Test emergency call executed: {call_result}")
        
        return {
            "status": "success",
            "message": "Emergency calling system tested",
            "demo_result": call_result,
            "note": "In production with TWILIO_ENABLED=true, real calls would be made"
        }
    
    except Exception as e:
        logger.error(f"Test call error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
