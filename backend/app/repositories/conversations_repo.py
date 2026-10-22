"""
app/repositories/conversations_repo.py
PyMongo repository for the conversations collection.
"""

import logging
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)

# Default cap: pulled from Config at runtime when needed
_DEFAULT_MAX_MESSAGES = 50


def _serialize(doc: dict) -> dict | None:
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def create_conversation(
    db, session_id: str, owner_id: str, topic_id: str | None = None
) -> dict:
    """
    Create a new conversation document for a session.

    Args:
        db: PyMongo database instance.
        session_id: Associated learning session ID string.
        owner_id: Owner identifier.
        topic_id: Optional topic identifier string.

    Returns:
        Created conversation document.
    """
    now = datetime.now(timezone.utc)
    doc = {
        "session_id": session_id,
        "owner_id": owner_id,
        "topic_id": topic_id,
        "messages": [],
        "created_at": now,
        "updated_at": now,
    }
    result = db.conversations.insert_one(doc)
    created = db.conversations.find_one({"_id": result.inserted_id})
    return _serialize(created)


def get_conversation_by_session(db, session_id: str) -> dict | None:
    """
    Return the conversation document for a given session.

    Args:
        db: PyMongo database instance.
        session_id: Learning session ID string.

    Returns:
        Conversation document or None.
    """
    doc = db.conversations.find_one({"session_id": session_id})
    return _serialize(doc) if doc else None


def append_message(
    db,
    conversation_id: str,
    message: dict,
    max_messages: int = _DEFAULT_MAX_MESSAGES,
) -> bool:
    """
    Append a message to the conversation, trimming oldest if over limit.

    Args:
        db: PyMongo database instance.
        conversation_id: Conversation ObjectId string.
        message: Message dict (role, content, timestamp).
        max_messages: Maximum number of messages to retain.

    Returns:
        True on success, False otherwise.
    """
    try:
        oid = ObjectId(conversation_id)
    except (InvalidId, TypeError):
        return False

    message.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

    # Push the new message, then slice to keep only the last max_messages
    result = db.conversations.update_one(
        {"_id": oid},
        {
            "$push": {
                "messages": {
                    "$each": [message],
                    "$slice": -max_messages,
                }
            },
            "$set": {"updated_at": datetime.now(timezone.utc)},
        },
    )
    return result.modified_count > 0


def get_recent_messages(db, conversation_id: str, limit: int = 10) -> list[dict]:
    """
    Return the last `limit` messages from a conversation.

    Args:
        db: PyMongo database instance.
        conversation_id: Conversation ObjectId string.
        limit: Number of recent messages to return.

    Returns:
        List of message dicts.
    """
    try:
        oid = ObjectId(conversation_id)
    except (InvalidId, TypeError):
        return []
    doc = db.conversations.find_one({"_id": oid}, {"messages": {"$slice": -limit}})
    if not doc:
        return []
    return doc.get("messages", [])


def delete_conversation(db, conversation_id: str, owner_id: str) -> bool:
    """
    Delete a conversation only if the owner_id matches.

    Args:
        db: PyMongo database instance.
        conversation_id: Conversation ObjectId string.
        owner_id: Claimed owner identifier.

    Returns:
        True if deleted, False otherwise.
    """
    try:
        oid = ObjectId(conversation_id)
    except (InvalidId, TypeError):
        return False
    result = db.conversations.delete_one({"_id": oid, "owner_id": owner_id})
    return result.deleted_count > 0
