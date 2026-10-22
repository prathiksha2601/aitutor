"""
tests/agents/test_agent_policies.py
Tests for EIT Learning Agent policy restrictions and security guards.
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from app.agents.policies import (
    check_tool_allowed,
    validate_agent_request,
    sanitize_expression_context,
)


def test_disallowed_tool_raises_permission_error():
    """CRITICAL AGENT SECURITY TEST: Block arbitrary tool execution."""
    disallowed_tools = [
        "execute_code",
        "run_shell",
        "drop_table",
        "read_secret_keys",
        "fetch_unauthorized_student",
    ]
    for tool_name in disallowed_tools:
        with pytest.raises(PermissionError):
            check_tool_allowed(tool_name)


def test_approved_tools_pass():
    approved = ["get_lesson", "get_topic", "get_conversation", "get_progress"]
    for tool_name in approved:
        # Should not raise
        check_tool_allowed(tool_name)


def test_invalid_request_type_rejected():
    with pytest.raises(ValueError):
        validate_agent_request("arbitrary_execution", "simple")


def test_invalid_response_mode_rejected():
    with pytest.raises(ValueError):
        validate_agent_request("chat", "unapproved_mode")


def test_sanitize_expression_context_strips_sensitive_data():
    raw_context = {
        "dominant_expression": "neutral",
        "confidence": 0.85,
        "observation_count": 8,
        "raw_image_data": b"sensitive_bytes",
        "face_embedding_vector": [0.1, 0.2, 0.3],
        "user_secret": "secret",
    }
    sanitized = sanitize_expression_context(raw_context)

    assert "raw_image_data" not in sanitized
    assert "face_embedding_vector" not in sanitized
    assert "user_secret" not in sanitized
    assert sanitized["dominant_expression"] == "neutral"
    assert sanitized["signal_nature"] == "uncertain_optional_signal"
