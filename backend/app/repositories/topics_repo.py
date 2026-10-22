"""
app/repositories/topics_repo.py
PyMongo repository for the topics collection.
"""

import logging
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)

_TOPIC_PROJECTION = {
    "_id": 1,
    "title": 1,
    "description": 1,
    "category": 1,
    "is_active": 1,
}


def _serialize(doc: dict) -> dict:
    """Convert ObjectId fields to strings for JSON serialisation."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def get_all_topics(db, page: int = 1, per_page: int = 20) -> list[dict]:
    """
    Return a paginated list of active topics.

    Args:
        db: PyMongo database instance.
        page: 1-indexed page number.
        per_page: Number of items per page.

    Returns:
        List of topic documents with string _id.
    """
    skip = (page - 1) * per_page
    cursor = (
        db.topics.find({"is_active": True}, _TOPIC_PROJECTION)
        .skip(skip)
        .limit(per_page)
    )
    return [_serialize(doc) for doc in cursor]


def get_topic_by_id(db, topic_id: str) -> dict | None:
    """
    Return a single topic by its ObjectId string.

    Args:
        db: PyMongo database instance.
        topic_id: Hex string ObjectId.

    Returns:
        Topic document or None.
    """
    try:
        oid = ObjectId(topic_id)
    except (InvalidId, TypeError):
        logger.warning("Invalid topic_id: %s", topic_id)
        return None
    doc = db.topics.find_one({"_id": oid}, _TOPIC_PROJECTION)
    return _serialize(doc) if doc else None


def count_topics(db) -> int:
    """Return the total count of active topics."""
    return db.topics.count_documents({"is_active": True})
