"""Unit tests for voice signal service heuristics."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.voice_signal_service import VoiceSignalService


def test_empty_audio_returns_zero_score():
    svc = VoiceSignalService()
    out = svc.analyze(b"")
    assert out["voice_risk_score"] == 0.0
    assert out["confidence"] == 0.0


def test_non_wav_audio_uses_payload_heuristic():
    svc = VoiceSignalService()
    out = svc.analyze(b"x" * 10000)
    assert 0.0 <= out["voice_risk_score"] <= 1.0
    assert out["method"] in {"payload_heuristic", "wav_rms_peak_zcr"}

