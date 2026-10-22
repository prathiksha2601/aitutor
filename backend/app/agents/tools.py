"""
app/agents/tools.py
Approved, restricted tools for the EIT Learning Agent.
LLM cannot call arbitrary functions or run arbitrary code.
"""

import logging
from app.agents.policies import check_tool_allowed
from app.repositories import lessons_repo, topics_repo, conversations_repo, progress_repo

logger = logging.getLogger(__name__)


def get_lesson_tool(db, lesson_id: str | None) -> dict | None:
    """Retrieve metadata for a specific lesson."""
    check_tool_allowed("get_lesson")
    if not lesson_id or db is None:
        return None
    try:
        return lessons_repo.get_lesson_by_id(db, lesson_id)
    except Exception as exc:
        logger.warning("get_lesson_tool error: %s", exc)
        return None


def get_topic_tool(db, topic_id: str | None) -> dict | None:
    """Retrieve metadata for a specific topic."""
    check_tool_allowed("get_topic")
    if not topic_id or db is None:
        return None
    try:
        return topics_repo.get_topic_by_id(db, topic_id)
    except Exception as exc:
        logger.warning("get_topic_tool error: %s", exc)
        return None


def get_conversation_tool(db, session_id: str, limit: int = 10) -> list[dict]:
    """Retrieve limited recent conversation messages."""
    check_tool_allowed("get_conversation")
    if not session_id or db is None:
        return []
    try:
        conv = conversations_repo.get_conversation_by_session(db, session_id)
        if not conv or "messages" not in conv:
            return []
        messages = conv["messages"]
        return messages[-limit:]
    except Exception as exc:
        logger.warning("get_conversation_tool error: %s", exc)
        return []


def get_progress_tool(db, owner_id: str, lesson_id: str | None) -> dict | None:
    """Retrieve student's progress on a lesson."""
    check_tool_allowed("get_progress")
    if not owner_id or not lesson_id or db is None:
        return None
    try:
        return progress_repo.get_lesson_progress(db, owner_id, lesson_id)
    except Exception as exc:
        logger.warning("get_progress_tool error: %s", exc)
        return None
