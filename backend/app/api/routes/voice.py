"""
Voice API routes for Phase 2 multimodal risk analysis.
"""
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import VoiceAnalysisResponse
from app.services.voice_signal_service import VoiceSignalService

router = APIRouter(prefix="/crisis", tags=["Crisis"])
voice_service = VoiceSignalService()


@router.post("/analyze-audio", response_model=VoiceAnalysisResponse)
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze uploaded audio and produce a voice risk score.
    Accepts common audio types; WAV receives richer analysis.
    """
    try:
        audio_bytes = await file.read()
        result = voice_service.analyze(audio_bytes)
        voice_risk_score = float(result["voice_risk_score"])
        return VoiceAnalysisResponse(
            voice_risk_score=voice_risk_score,
            voice_crisis_detected=voice_risk_score >= 0.70,
            confidence=float(result["confidence"]),
            method=str(result["method"]),
            details=result.get("details", {}),
            status="success",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to analyze audio: {exc}") from exc

