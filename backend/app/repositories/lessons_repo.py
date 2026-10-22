"""
app/repositories/lessons_repo.py
PyMongo repository for the lessons collection.
"""

import logging
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)

_LESSON_PROJECTION = {
    "content_internal": 0,  # exclude any internal-only fields
}


def _serialize(doc: dict) -> dict:
    """Convert ObjectId fields to strings."""
    if doc is None:
        return None
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    if "topic_id" in doc and isinstance(doc["topic_id"], ObjectId):
        doc["topic_id"] = str(doc["topic_id"])
    return doc


def get_lessons_by_topic(
    db, topic_id: str, page: int = 1, per_page: int = 20
) -> list[dict]:
    """
    Return paginated published lessons for a topic, sorted by sequence_number.

    Args:
        db: PyMongo database instance.
        topic_id: Topic's ObjectId string.
        page: 1-indexed page number.
        per_page: Items per page.

    Returns:
        List of lesson documents.
    """
    try:
        oid = ObjectId(topic_id)
    except (InvalidId, TypeError):
        logger.warning("Invalid topic_id for lessons query: %s", topic_id)
        return []
    skip = (page - 1) * per_page
    cursor = (
        db.lessons.find(
            {"topic_id": oid, "is_published": True},
            _LESSON_PROJECTION,
        )
        .sort("sequence_number", 1)
        .skip(skip)
        .limit(per_page)
    )
    return [_serialize(doc) for doc in cursor]


def get_lesson_by_id(db, lesson_id: str) -> dict | None:
    """
    Return a single lesson by its ObjectId string.

    Args:
        db: PyMongo database instance.
        lesson_id: Hex string ObjectId.

    Returns:
        Lesson document or None.
    """
    try:
        oid = ObjectId(lesson_id)
    except (InvalidId, TypeError):
        logger.warning("Invalid lesson_id: %s", lesson_id)
        return None
    doc = db.lessons.find_one({"_id": oid}, _LESSON_PROJECTION)
    return _serialize(doc) if doc else None


def get_all_lessons(db, page: int = 1, per_page: int = 50) -> list[dict]:
    """
    Return all published lessons paginated.

    Args:
        db: PyMongo database instance.
        page: 1-indexed page number.
        per_page: Items per page (max 50).

    Returns:
        List of lesson documents.
    """
    skip = (page - 1) * per_page
    cursor = (
        db.lessons.find({"is_published": True}, _LESSON_PROJECTION)
        .sort("sequence_number", 1)
        .skip(skip)
        .limit(per_page)
    )
    return [_serialize(doc) for doc in cursor]


def count_lessons_by_topic(db, topic_id: str) -> int:
    """Return count of published lessons for a topic."""
    try:
        oid = ObjectId(topic_id)
    except (InvalidId, TypeError):
        return 0
    return db.lessons.count_documents({"topic_id": oid, "is_published": True})
