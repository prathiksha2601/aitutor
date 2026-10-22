"""
app/repositories/quiz_repo.py
PyMongo repository for the quiz_attempts collection.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _serialize(doc: dict) -> dict | None:
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def create_quiz_attempt(db, attempt_data: dict) -> dict:
    """
    Insert a new quiz attempt record.

    Args:
        db: PyMongo database instance.
        attempt_data: Attempt document to insert.

    Returns:
        Created quiz attempt document with string _id.
    """
    attempt_data["created_at"] = datetime.now(timezone.utc)
    result = db.quiz_attempts.insert_one(attempt_data)
    doc = db.quiz_attempts.find_one({"_id": result.inserted_id})
    return _serialize(doc)


def get_attempts_by_owner(
    db, owner_id: str, page: int = 1, per_page: int = 20
) -> list[dict]:
    """
    Return paginated quiz attempts for an owner.

    Args:
        db: PyMongo database instance.
        owner_id: User or anonymous session identifier.
        page: 1-indexed page number.
        per_page: Items per page.

    Returns:
        List of quiz attempt documents.
    """
    skip = (page - 1) * per_page
    cursor = (
        db.quiz_attempts.find({"owner_id": owner_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(per_page)
    )
    return [_serialize(doc) for doc in cursor]
