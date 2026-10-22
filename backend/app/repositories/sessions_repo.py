"""
app/repositories/sessions_repo.py
PyMongo repository for the learning_sessions collection.
"""

import logging
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)


def _serialize(doc: dict) -> dict | None:
    """Convert ObjectId fields to strings."""
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    for field in ("user_id", "lesson_id", "topic_id"):
        if field in doc and isinstance(doc[field], ObjectId):
            doc[field] = str(doc[field])
    return doc


def create_session(db, session_data: dict) -> dict:
    """
    Insert a new learning session.

    Args:
        db: PyMongo database instance.
        session_data: Session document to insert.

    Returns:
        Created session document with string _id.
    """
    session_data["created_at"] = datetime.now(timezone.utc)
    session_data["updated_at"] = datetime.now(timezone.utc)
    session_data.setdefault("status", "active")
    result = db.learning_sessions.insert_one(session_data)
    doc = db.learning_sessions.find_one({"_id": result.inserted_id})
    return _serialize(doc)


def get_session_by_id(db, session_id: str) -> dict | None:
    """
    Return a session by its ObjectId string.

    Args:
        db: PyMongo database instance.
        session_id: Hex string ObjectId.

    Returns:
        Session document or None.
    """
    try:
        oid = ObjectId(session_id)
    except (InvalidId, TypeError):
        return None
    doc = db.learning_sessions.find_one({"_id": oid})
    return _serialize(doc) if doc else None


def update_session(db, session_id: str, update_data: dict) -> dict | None:
    """
    Update allowed fields of a session and return the updated document.

    Args:
        db: PyMongo database instance.
        session_id: Hex string ObjectId.
        update_data: Fields to update.

    Returns:
        Updated session document or None.
    """
    try:
        oid = ObjectId(session_id)
    except (InvalidId, TypeError):
        return None
    update_data["updated_at"] = datetime.now(timezone.utc)
    db.learning_sessions.update_one({"_id": oid}, {"$set": update_data})
    doc = db.learning_sessions.find_one({"_id": oid})
    return _serialize(doc) if doc else None


def end_session(db, session_id: str) -> dict | None:
    """
    Mark a session as completed and record the end time.

    Args:
        db: PyMongo database instance.
        session_id: Hex string ObjectId.

    Returns:
        Updated session document or None.
    """
    return update_session(
        db,
        session_id,
        {"status": "completed", "ended_at": datetime.now(timezone.utc)},
    )


def get_sessions_by_owner(
    db, owner_id: str, page: int = 1, per_page: int = 20
) -> list[dict]:
    """
    Return paginated sessions belonging to an owner.

    Args:
        db: PyMongo database instance.
        owner_id: User ID or anonymous session ID string.
        page: 1-indexed page number.
        per_page: Items per page.

    Returns:
        List of session documents.
    """
    skip = (page - 1) * per_page
    cursor = (
        db.learning_sessions.find({"owner_id": owner_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(per_page)
    )
    return [_serialize(doc) for doc in cursor]


def verify_session_ownership(db, session_id: str, owner_id: str) -> bool:
    """
    CRITICAL security check: verify that owner_id owns the session.

    Args:
        db: PyMongo database instance.
        session_id: Session's ObjectId string.
        owner_id: Claimed owner identifier.

    Returns:
        True only if the session exists and owner_id matches.
    """
    try:
        oid = ObjectId(session_id)
    except (InvalidId, TypeError):
        return False
    doc = db.learning_sessions.find_one(
        {"_id": oid, "$or": [{"user_id": owner_id}, {"owner_id": owner_id}]},
        {"_id": 1},
    )
    return doc is not None
