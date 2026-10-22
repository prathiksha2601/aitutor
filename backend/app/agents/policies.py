"""
app/agents/policies.py
Policy enforcement for the EIT Learning Agent:
Allowlisted tools, request validation, and privacy protection for expression signals.
"""

import logging

logger = logging.getLogger(__name__)

ALLOWED_TOOLS = {
    "get_lesson",
    "get_topic",
    "get_conversation",
    "get_progress",
}

ALLOWED_REQUEST_TYPES = {
    "chat",
    "explain",
    "quiz",
    "feedback",
    "summary",
    "revision",
}

ALLOWED_RESPONSE_MODES = {
    "simple",
    "step_by_step",
    "example",
    "programming",
    "quiz",
    "feedback",
    "summary",
    "revision",
}


def check_tool_allowed(tool_name: str) -> None:
    """Ensure agent is only invoking allowlisted tools."""
    if tool_name not in ALLOWED_TOOLS:
        logger.warning("Agent attempted disallowed tool: %s", tool_name)
        raise PermissionError(f"Tool '{tool_name}' is not in the approved agent tools list.")


def validate_agent_request(request_type: str, response_mode: str) -> None:
    """Validate request type and response mode."""
    if request_type not in ALLOWED_REQUEST_TYPES:
        raise ValueError(f"Invalid request type: '{request_type}'. Allowed: {ALLOWED_REQUEST_TYPES}")
    if response_mode not in ALLOWED_RESPONSE_MODES:
        raise ValueError(f"Invalid response mode: '{response_mode}'. Allowed: {ALLOWED_RESPONSE_MODES}")


def sanitize_expression_context(ctx: dict | None) -> dict | None:
    """
    Sanitize expression context.
    Ensures no raw images, facial embeddings, or identifying information are included.
    Labels data as an uncertain, secondary signal.
    """
    if not ctx:
        return None
    allowed_keys = {
        "dominant_expression",
        "confidence",
        "observation_count",
        "suggested_support",
    }
    sanitized = {k: v for k, v in ctx.items() if k in allowed_keys}
    sanitized["signal_nature"] = "uncertain_optional_signal"
    return sanitized
