"""
Crisis fusion layer — combines text, future voice, and other signals into one crisis decision.
Phase 1: text-only passthrough; voice and other modalities plug in here later.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CrisisFusionService:
    """Fuses multimodal crisis indicators."""

    _instance: Optional["CrisisFusionService"] = None

    def __new__(cls):
        if cls._instance is None:
            inst = super().__new__(cls)
            inst._initialized = False
            cls._instance = inst
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        logger.info("Initializing CrisisFusionService (multimodal mode)")
        self._initialized = True

    def fuse(
        self,
        *,
        text_crisis_detected: bool,
        prediction: Optional[str],
        probabilities: Dict[str, float],
        voice_crisis_detected: Optional[bool] = None,
        voice_risk_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Returns crisis_detected plus explainable metadata for clients and research.

        Weighted fusion for Phase 2:
        - text score from Suicidal probability (or text crisis bool fallback)
        - optional voice score/flag
        - conservative high-risk override for explicit voice crisis flag
        """
        sources = ["text"]
        text_score = float(probabilities.get("Suicidal", 1.0 if text_crisis_detected else 0.0))
        crisis = bool(text_crisis_detected)
        fused_risk_score: Optional[float] = text_score
        resolved_voice_score: Optional[float] = voice_risk_score

        if resolved_voice_score is None and voice_crisis_detected is not None:
            resolved_voice_score = 1.0 if voice_crisis_detected else 0.0

        if resolved_voice_score is not None:
            sources.append("voice")
            fused_risk_score = (0.7 * text_score) + (0.3 * float(resolved_voice_score))
            crisis = (
                crisis
                or bool(voice_crisis_detected)
                or float(resolved_voice_score) >= 0.75
                or float(fused_risk_score) >= 0.60
            )

        return {
            "crisis_detected": crisis,
            "sources": sources,
            "text_crisis": bool(text_crisis_detected),
            "voice_crisis": voice_crisis_detected,
            "text_risk_score": text_score,
            "voice_risk_score": resolved_voice_score,
            "fused_risk_score": fused_risk_score,
        }


def get_crisis_fusion_service() -> CrisisFusionService:
    """FastAPI dependency provider."""
    return CrisisFusionService()
