"""
Emergency Service - Handles automatic crisis calling via Twilio
Phase 2: Automatic emergency response to high-risk crisis situations
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.core.config import settings
from app.models.database import EmergencyCall, EmergencyContact

logger = logging.getLogger(__name__)


class EmergencyService:
    """Manages emergency calling and crisis response automation"""

    _instance: Optional["EmergencyService"] = None
    _twilio_client: Optional[Any] = None

    def __new__(cls):
        if cls._instance is None:
            inst = super().__new__(cls)
            inst._initialized = False
            cls._instance = inst
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        
        logger.info("Initializing Emergency Service")
        self._initialized = True
        
        # Initialize Twilio client if enabled
        if settings.TWILIO_ENABLED:
            try:
                from twilio.rest import Client
                self._twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self._twilio_client = None
        else:
            logger.info("Twilio calling disabled (set TWILIO_ENABLED=True to enable)")

    async def should_trigger_emergency_call(
        self,
        fused_risk_score: Optional[float],
        text_risk_score: float,
        voice_risk_score: Optional[float],
        crisis_detected: bool,
        prediction: str,
    ) -> bool:
        """
        Determine if an emergency call should be triggered.
        
        Args:
            fused_risk_score: Combined risk score from multimodal fusion
            text_risk_score: Risk score from text analysis
            voice_risk_score: Risk score from voice analysis
            crisis_detected: Whether crisis fusion detected something
            prediction: ML prediction label
            
        Returns:
            True if emergency call should be triggered
        """
        # Critical criteria for automatic emergency call
        criteria_met = []
        
        # 1. High fused risk score
        if fused_risk_score is not None and fused_risk_score >= settings.EMERGENCY_CALL_THRESHOLD:
            criteria_met.append(f"fused_risk_score ({fused_risk_score:.2f}) >= {settings.EMERGENCY_CALL_THRESHOLD}")
        
        # 2. Text explicitly shows suicidal intent
        if prediction == "Suicidal" and text_risk_score >= 0.80:
            criteria_met.append(f"Suicidal prediction with high confidence ({text_risk_score:.2f})")
        
        # 3. Combined text + voice both elevated
        if (text_risk_score >= 0.70 and voice_risk_score is not None and voice_risk_score >= 0.70):
            criteria_met.append(f"Both text ({text_risk_score:.2f}) and voice ({voice_risk_score:.2f}) elevated")
        
        should_call = len(criteria_met) > 0
        
        if should_call:
            logger.warning(f"Emergency call criteria met: {', '.join(criteria_met)}")
        
        return should_call

    async def trigger_emergency_call(
        self,
        user_id: int,
        conversation_id: int,
        message_id: Optional[int],
        fused_risk_score: Optional[float],
        text_risk_score: float,
        voice_risk_score: Optional[float],
        prediction: str,
        emergency_contacts: Optional[List[EmergencyContact]] = None,
        db_session: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Trigger emergency call(s) to emergency contacts or crisis hotlines.
        
        Args:
            user_id: User ID in crisis
            conversation_id: Conversation where crisis was detected
            message_id: Message that triggered crisis
            fused_risk_score: Combined risk score
            text_risk_score: Text risk score
            voice_risk_score: Voice risk score
            prediction: ML prediction
            emergency_contacts: User's emergency contacts (optional)
            db_session: Database session for logging
            
        Returns:
            Dict with call status and SIDs
        """
        result = {
            "emergency_calls_triggered": False,
            "calls": [],
            "status": "success",
            "message": "No calls needed"
        }
        
        # Early return if Twilio not enabled
        if not settings.TWILIO_ENABLED or not self._twilio_client:
            logger.warning("Twilio not enabled or client unavailable - would trigger call in production")
            result["message"] = "DEMO MODE: Emergency call would be triggered in production"
            return result
        
        try:
            # Determine numbers to call
            numbers_to_call = []
            
            # Priority 1: User's personal emergency contacts
            if emergency_contacts:
                active_contacts = [c for c in emergency_contacts if c.is_active]
                for contact in active_contacts[:3]:  # Limit to 3 contacts
                    numbers_to_call.append({
                        "number": contact.phone_number,
                        "name": contact.name,
                        "type": "personal_contact",
                        "contact_id": contact.id
                    })
            
            # Priority 2: Default crisis hotlines if no personal contacts
            if not numbers_to_call:
                for hotline in settings.DEFAULT_CRISIS_HOTLINES:
                    numbers_to_call.append({
                        "number": hotline,
                        "name": "Crisis Hotline",
                        "type": "hotline",
                        "contact_id": None
                    })
            
            # Make calls
            for target in numbers_to_call:
                try:
                    call = await self._make_call(
                        from_number=settings.TWILIO_PHONE_NUMBER,
                        to_number=target["number"],
                        user_id=user_id,
                        conversation_id=conversation_id,
                        fused_risk_score=fused_risk_score,
                        prediction=prediction,
                    )
                    
                    # Log call to database
                    if db_session:
                        await self._log_emergency_call(
                            db_session=db_session,
                            user_id=user_id,
                            conversation_id=conversation_id,
                            phone_number=target["number"],
                            call_sid=call.get("sid"),
                            emergency_contact_id=target["contact_id"],
                            fused_risk_score=fused_risk_score,
                            text_risk_score=text_risk_score,
                            voice_risk_score=voice_risk_score,
                            crisis_type=prediction,
                            message_id=message_id,
                        )
                    
                    result["calls"].append({
                        "target": target["name"],
                        "number": target["number"],
                        "call_sid": call.get("sid"),
                        "status": call.get("status")
                    })
                    result["emergency_calls_triggered"] = True
                    
                    logger.warning(f"Emergency call triggered to {target['name']} ({target['number']}) for user {user_id}")
                    
                except Exception as call_error:
                    logger.error(f"Failed to call {target['number']}: {call_error}")
                    result["calls"].append({
                        "target": target["name"],
                        "number": target["number"],
                        "error": str(call_error)
                    })
            
            if result["emergency_calls_triggered"]:
                result["message"] = f"Emergency calls initiated to {len(result['calls'])} contact(s)"
                logger.critical(f"EMERGENCY CALLS MADE for user {user_id} due to crisis detection")
            else:
                result["status"] = "error"
                result["message"] = "Failed to make emergency calls"
                
        except Exception as e:
            logger.error(f"Emergency service error: {e}", exc_info=True)
            result["status"] = "error"
            result["message"] = str(e)
        
        return result

    async def _make_call(
        self,
        from_number: str,
        to_number: str,
        user_id: int,
        conversation_id: int,
        fused_risk_score: Optional[float],
        prediction: str,
    ) -> Dict[str, Any]:
        """
        Core Twilio call initiation.
        
        Returns:
            Dict with call SID and status
        """
        try:
            # TwiML (Twilio Markup Language) for the call
            twiml_message = self._generate_crisis_twiml(
                user_id=user_id,
                fused_risk_score=fused_risk_score,
                prediction=prediction,
            )
            
            call = self._twilio_client.calls.create(
                to=to_number,
                from_=from_number,
                twiml=twiml_message,
                timeout=settings.EMERGENCY_CALL_TIMEOUT,
                record=False,
                status_callback=None,  # Could add webhook for status updates
            )
            
            return {
                "sid": call.sid,
                "status": "initiated",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Twilio call failed: {e}")
            raise

    def _generate_crisis_twiml(
        self,
        user_id: int,
        fused_risk_score: Optional[float],
        prediction: str,
    ) -> str:
        """
        Generate Twilio markup for crisis support call message.
        
        Returns:
            TwiML XML string for Twilio
        """
        score_text = f"with a risk score of {fused_risk_score:.0%}" if fused_risk_score else ""
        
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        This is an urgent message from Serenity Mental Health Crisis Response System.
        A person has been identified as being in crisis {score_text}.
        If you are the person in crisis, please know that help is available.
        If you are an emergency contact, please respond to assist.
        Connecting you to crisis support services now.
    </Say>
    <Dial>+19882255247</Dial>
</Response>"""
        
        return twiml

    async def _log_emergency_call(
        self,
        db_session: Any,
        user_id: int,
        conversation_id: int,
        phone_number: str,
        call_sid: Optional[str],
        emergency_contact_id: Optional[int],
        fused_risk_score: Optional[float],
        text_risk_score: float,
        voice_risk_score: Optional[float],
        crisis_type: str,
        message_id: Optional[int],
    ) -> None:
        """Log emergency call to database for audit trail"""
        try:
            emergency_call = EmergencyCall(
                user_id=user_id,
                conversation_id=conversation_id,
                emergency_contact_id=emergency_contact_id,
                phone_number=phone_number,
                call_sid=call_sid,
                status="initiated",
                crisis_type=crisis_type,
                fused_risk_score=fused_risk_score,
                text_risk_score=text_risk_score,
                voice_risk_score=voice_risk_score,
                message_id=message_id,
                call_initiated_at=datetime.utcnow(),
                call_metadata={
                    "threshold": settings.EMERGENCY_CALL_THRESHOLD,
                    "trigger_type": "automatic_crisis_response"
                }
            )
            db_session.add(emergency_call)
            await db_session.flush()
            logger.info(f"Emergency call logged: {emergency_call.id} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log emergency call: {e}")


def get_emergency_service() -> EmergencyService:
    """FastAPI dependency provider"""
    return EmergencyService()
