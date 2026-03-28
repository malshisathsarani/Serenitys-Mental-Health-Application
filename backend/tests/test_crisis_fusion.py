"""Tests for crisis fusion service (Phase 1 text-only)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.crisis_fusion_service import CrisisFusionService


def test_fuse_text_only_passthrough():
    svc = CrisisFusionService()
    out = svc.fuse(
        text_crisis_detected=True,
        prediction="Suicidal",
        probabilities={"Suicidal": 0.9},
    )
    assert out["crisis_detected"] is True
    assert out["sources"] == ["text"]
    assert out["text_crisis"] is True
    assert out["voice_crisis"] is None


def test_fuse_voice_or_combines():
    svc = CrisisFusionService()
    out = svc.fuse(
        text_crisis_detected=False,
        prediction="Normal",
        probabilities={},
        voice_crisis_detected=True,
    )
    assert out["crisis_detected"] is True
    assert "voice" in out["sources"]
