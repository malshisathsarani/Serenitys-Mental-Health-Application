"""Schema tests for feedback payload validation."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.schemas import FeedbackRequest


def test_feedback_request_valid():
    req = FeedbackRequest(message_id=10, helpful=False, comment="Bias detected")
    assert req.message_id == 10
    assert req.helpful is False


def test_feedback_request_rejects_invalid_message_id():
    with pytest.raises(Exception):
        FeedbackRequest(message_id=0, helpful=True)

