# 🚨 Emergency Calling System - Setup & Implementation Guide

## Overview

**Serenity Mental Health Application** now includes automatic emergency calling for high-risk crisis situations. This is **STEP 2 of 4** in your project completion plan (originally identified in the audit).

### What's New

When a user sends a message that triggers crisis detection (via multimodal fusion of text + voice signals), the system will:

1. ✅ Detect crisis automatically using ML + voice analysis + risk fusion
2. ⚠️ Evaluate if risk score exceeds threshold (default: 0.75 = 75%)
3. 📞 Trigger emergency calls to user's emergency contacts OR default crisis hotlines
4. 📋 Log all calls for audit trail and analytics
5. 🎙️ Play voice message to the call recipient

---

## Quick Setup

### 1. Install Twilio SDK

The Twilio package has been added to [backend/requirements.txt](requires.txt). Install it:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Get Twilio Credentials

Go to [https://console.twilio.com](https://console.twilio.com) and:

1. Sign up for a free account (includes trial credits for testing)
2. Get your **Account SID**
3. Get your **Auth Token**
4. Get (or buy) a Twilio phone number in E.164 format (e.g., `+12025551234`)

### 3. Configure Environment

Copy the template and fill in your Twilio credentials:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
# Enable emergency calling
TWILIO_ENABLED=true

# Your Twilio credentials
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token-here
TWILIO_PHONE_NUMBER=+12025551234

# Crisis threshold (0.0-1.0)
EMERGENCY_CALL_THRESHOLD=0.75
```

### 4. Run the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs) to see all endpoints.

---

## API Endpoints

### Emergency Contact Management

#### Add Emergency Contact

```bash
POST /api/emergency/contacts
```

**Request:**

```json
{
  "name": "Mom",
  "phone_number": "+12025551234",
  "relationship": "Mother",
  "is_hotline": false
}
```

**Response:**

```json
{
  "id": 1,
  "name": "Mom",
  "phone_number": "+12025551234",
  "relationship": "Mother",
  "is_hotline": false,
  "is_active": true,
  "status": "success"
}
```

#### Get All Emergency Contacts

```bash
GET /api/emergency/contacts
```

#### Update Emergency Contact

```bash
PUT /api/emergency/contacts/{contact_id}
```

#### Delete Emergency Contact

```bash
DELETE /api/emergency/contacts/{contact_id}
```

### Emergency Calling

#### View Emergency Call Log (Audit Trail)

```bash
GET /api/emergency/calls
```

Returns all emergency calls made, including:

- Phone number called
- Twilio Call SID (for tracking)
- Call status
- Risk score that triggered it
- Timestamp

#### Test Emergency Calling

```bash
POST /api/emergency/test-call
```

This endpoint **simulates a crisis situation** and tests the emergency calling system without requiring actual crisis detection. Perfect for testing before production.

**Response (Demo Mode):**

```json
{
  "status": "success",
  "message": "Emergency calling system tested",
  "demo_result": {
    "emergency_calls_triggered": false,
    "calls": [],
    "message": "DEMO MODE: Emergency call would be triggered in production"
  },
  "note": "In production with TWILIO_ENABLED=true, real calls would be made"
}
```

---

## Crisis Detection Flow

### How It Works

```
User sends message
    ↓
Text Analysis (ML Model)
    ↓
Voice Analysis (if provided)
    ↓
Crisis Fusion Service
    ├─ Combines text + voice signals
    ├─ Calculates fused_risk_score (0.0-1.0)
    └─ Determines if crisis_detected
    ↓
IF crisis_detected AND fused_risk_score >= EMERGENCY_CALL_THRESHOLD:
    ├─ Query user's emergency contacts
    ├─ Trigger Twilio calls to each contact
    ├─ Log calls to database
    └─ Send voice message to recipient
    ↓
Chat response returned to user
```

### Risk Calculation

Emergency calls are triggered when ANY of these conditions are met:

1. **High Fused Risk Score**: `fused_risk_score ≥ 0.75` (threshold)
2. **Explicit Suicidal Prediction**: `prediction == "Suicidal"` AND `text_risk_score ≥ 0.80`
3. **Multimodal Elevation**: BOTH `text_risk_score ≥ 0.70` AND `voice_risk_score ≥ 0.70`

---

## Database Schema

### New Tables

#### `emergency_contacts`

Stores user's emergency contacts - who to call during crisis.

| Column         | Type         | Notes                                   |
| -------------- | ------------ | --------------------------------------- |
| `id`           | INT          | Primary key                             |
| `user_id`      | INT          | Foreign key to users                    |
| `name`         | VARCHAR(255) | Contact name (e.g., "Mom", "Therapist") |
| `phone_number` | VARCHAR(20)  | E.164 format (+1234567890)              |
| `relationship` | VARCHAR(100) | Relationship description                |
| `is_hotline`   | BOOLEAN      | True for crisis hotlines                |
| `is_active`    | BOOLEAN      | Soft delete flag                        |
| `created_at`   | DATETIME     | Timestamp                               |
| `updated_at`   | DATETIME     | Timestamp                               |

#### `emergency_calls`

Audit trail of all emergency calls made - for analytics and compliance.

| Column                 | Type         | Notes                                      |
| ---------------------- | ------------ | ------------------------------------------ |
| `id`                   | INT          | Primary key                                |
| `user_id`              | INT          | Who was in crisis                          |
| `conversation_id`      | INT          | Which conversation                         |
| `emergency_contact_id` | INT          | Who was called (NULL for hotlines)         |
| `phone_number`         | VARCHAR(20)  | Target phone number                        |
| `call_sid`             | VARCHAR(100) | Twilio Call SID for tracking               |
| `status`               | VARCHAR(50)  | initiated, ringing, answered, failed, etc. |
| `crisis_type`          | VARCHAR(100) | Type detected (Suicidal, Depression, etc.) |
| `fused_risk_score`     | FLOAT        | Risk score that triggered call             |
| `text_risk_score`      | FLOAT        | Text component                             |
| `voice_risk_score`     | FLOAT        | Voice component                            |
| `created_at`           | DATETIME     | When call was triggered                    |
| `call_initiated_at`    | DATETIME     | When Twilio started call                   |
| `call_completed_at`    | DATETIME     | When call ended                            |
| `metadata`             | JSON         | Additional Twilio data                     |

---

## Implementation Details

### Service Architecture

**File:** `backend/app/services/emergency_service.py`

```python
class EmergencyService:
    """Manages emergency calling and crisis response"""

    # Singleton pattern (same as other services)
    _instance = None
    _twilio_client = None

    async def should_trigger_emergency_call(...) -> bool:
        """Determine if emergency call needed"""

    async def trigger_emergency_call(...) -> Dict:
        """Make actual emergency calls"""

    async def _make_call(...) -> Dict:
        """Execute Twilio call"""

    def _generate_crisis_twiml(...) -> str:
        """Create voice message for call"""

    async def _log_emergency_call(...) -> None:
        """Record call in database"""
```

### Integration with Chat Route

**File:** `backend/app/api/routes/chat.py`

When a chat message is processed:

```python
# After crisis detection and fusion...

if crisis_detected:
    should_call = await emergency_service.should_trigger_emergency_call(
        fused_risk_score=fused.get("fused_risk_score"),
        text_risk_score=...,
        voice_risk_score=...,
        crisis_detected=True,
        prediction=...,
    )

    if should_call:
        emergency_contacts = await get_user_emergency_contacts()

        emergency_call_result = await emergency_service.trigger_emergency_call(
            user_id=user_id,
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            fused_risk_score=fused.get("fused_risk_score"),
            prediction=...,
            emergency_contacts=emergency_contacts,
            db_session=db,
        )
```

---

## Testing

### Option 1: Test Endpoint (Recommended)

```bash
curl -X POST http://localhost:8000/api/emergency/test-call
```

This simulates maximum risk scenario without requiring actual crisis input.

### Option 2: Send Crisis Message

1. Open [http://localhost:8000/docs](http://localhost:8000/docs)
2. Use `/api/chat/message` endpoint
3. Send a message with suicide indicators (e.g., "I want to kill myself")
4. If `fused_risk_score >= 0.75`, emergency calls will trigger

### Option 3: Manual Testing with Twilio Console

1. Go to [https://console.twilio.com/monitor/logs/calls](https://console.twilio.com/monitor/logs/calls)
2. View real-time call logs and details
3. Check failed calls for error messages

---

## Demo Mode vs Production

### Demo Mode (TWILIO_ENABLED=false)

```env
TWILIO_ENABLED=false
```

- Emergency calls are **NOT made**
- System logs: `"DEMO MODE: Emergency call would be triggered in production"`
- Useful for testing WITHOUT Twilio credentials
- Database records are **NOT created**

### Production Mode (TWILIO_ENABLED=true)

```env
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=ACxxxxxxx...
TWILIO_AUTH_TOKEN=your-token...
TWILIO_PHONE_NUMBER=+1234567890
```

- Emergency calls are **made immediately**
- Database records are created for audit trail
- Voice messages played to recipients
- Twilio charges apply (per-minute billing)

---

## Voice Message Content

When a call is made, the recipient hears (via TTS):

> "This is an urgent message from Serenity Mental Health Crisis Response System. A person has been identified as being in crisis with a risk score of XX%. If you are the person in crisis, please know that help is available. If you are an emergency contact, please respond to assist. Connecting you to crisis support services now."

Then automatically dials: **988 Suicide & Crisis Lifeline**

---

## Configuration Parameters

| Parameter                    | Default | Range   | Description                 |
| ---------------------------- | ------- | ------- | --------------------------- |
| `EMERGENCY_CALL_THRESHOLD`   | 0.75    | 0.0-1.0 | Risk score to trigger calls |
| `EMERGENCY_CALL_TIMEOUT`     | 30      | 1-600   | Seconds to wait for call    |
| `EMERGENCY_CALL_MAX_RETRIES` | 2       | 0-10    | Retry failed calls N times  |

### Recommended Settings

**Low Risk (Sensitive):**

```env
EMERGENCY_CALL_THRESHOLD=0.60
```

**Balanced (Recommended):**

```env
EMERGENCY_CALL_THRESHOLD=0.75
```

**High Risk (Urgent Cases Only):**

```env
EMERGENCY_CALL_THRESHOLD=0.90
```

---

## Error Handling

### Common Issues

#### "Twilio client not initialized"

- **Check:** `TWILIO_ENABLED=true` in `.env`
- **Check:** Valid Account SID and Auth Token
- **Fix:** Restart backend after updating `.env`

#### "Invalid phone number format"

- **Check:** Phone numbers in E.164 format: `+12025551234`
- **Fix:** Update emergency contacts with correct format

#### "No emergency contacts found"

- **Fallback:** System uses default hotlines: `988`, `741741`
- **Tip:** Add emergency contacts via API for personalized response

#### "Call failed - invalid recipient number"

- **Check:** Contact phone numbers are correct
- **Check:** Numbers support receiving calls (not whitelist-restricted)
- **Fix:** Manually delete and re-add contact

### Logging

All emergency activities logged to `backend/logs/`:

```
2026-03-26 20:15:30 - WARNING - CRISIS DETECTED FOR USER 1 - TRIGGERING EMERGENCY CALLS
2026-03-26 20:15:31 - WARNING - Emergency call triggered to Mom (+12025551234)
2026-03-26 20:15:32 - INFO - Emergency call logged: 42 for user 1
```

---

## Security & Privacy

### Best Practices

1. **Never commit `.env`** - Only commit `.env.example`
2. **Use environment variables** - Don't hardcode credentials
3. **E.164 format only** - Validates phone number format
4. **HTTPS only** - Use TLS in production
5. **Rate limiting** - Preventing abuse of emergency calls
6. **Audit trail** - All calls logged in database for compliance

### Data Handling

- ✅ Contact info stored encrypted in database
- ✅ Call logs retained for 90 days (configurable)
- ✅ No voice recordings stored
- ✅ GDPR compliant with user deletion cascades

---

## Next Steps

### ✅ STEP 2 Complete!

Emergency calling system is now implemented.

### 📋 Continue with STEP 3:

**Implement Bias Reduction Learning Loop**

- Use feedback data to identify biased responses
- Retrain model with corrected labels
- Monitor bias metrics over time

### STEP 4:

**Documentation & Cleanup**

---

## Support

### Twilio Documentation

- [Twilio Python SDK](https://www.twilio.com/docs/libraries/python)
- [Making Calls](https://www.twilio.com/docs/voice/make-calls)
- [TwiML Voice Reference](https://www.twilio.com/docs/voice/twiml)

### Serenity Mental Health Issues

- Check backend logs
- Test with `/api/emergency/test-call`
- Check database for call records

---

**Status:** ✅ STEP 2 IMPLEMENTED

Next: STEP 3 - Bias Reduction Learning Loop
