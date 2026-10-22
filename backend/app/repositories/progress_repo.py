"""
app/repositories/progress_repo.py
PyMongo repository for the progress collection.
"""

import logging
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)


def _serialize(doc: dict) -> dict | None:
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def upsert_progress(db, progress_data: dict) -> dict:
    """
    Upsert a progress record keyed on (owner_id, lesson_id, topic_id).

    Args:
        db: PyMongo database instance.
        progress_data: Dict containing owner_id, lesson_id, topic_id and progress fields.

    Returns:
        Upserted progress document.
    """
    filter_query = {
        "owner_id": progress_data["owner_id"],
        "lesson_id": progress_data["lesson_id"],
        "topic_id": progress_data["topic_id"],
    }
    now = datetime.now(timezone.utc)
    update_fields = {k: v for k, v in progress_data.items() if k not in filter_query}
    update_fields["updated_at"] = now

    result = db.progress.find_one_and_update(
        filter_query,
        {
            "$set": update_fields,
            "$setOnInsert": {"created_at": now, **filter_query},
        },
        upsert=True,
        return_document=True,
    )
    return _serialize(result)


def get_progress_by_owner(
    db, owner_id: str, page: int = 1, per_page: int = 50
) -> list[dict]:
    """
    Return all progress records for an owner, paginated.

    Args:
        db: PyMongo database instance.
        owner_id: User or anonymous session identifier.
        page: 1-indexed page number.
        per_page: Items per page.

    Returns:
        List of progress documents.
    """
    skip = (page - 1) * per_page
    cursor = (
        db.progress.find({"owner_id": owner_id})
        .sort("updated_at", -1)
        .skip(skip)
        .limit(per_page)
    )
    return [_serialize(doc) for doc in cursor]


def get_lesson_progress(db, owner_id: str, lesson_id: str) -> dict | None:
    """
    Return the progress record for a specific lesson.

    Args:
        db: PyMongo database instance.
        owner_id: User or anonymous session identifier.
        lesson_id: Lesson identifier string.

    Returns:
        Progress document or None.
    """
    doc = db.progress.find_one({"owner_id": owner_id, "lesson_id": lesson_id})
    return _serialize(doc) if doc else None


def get_topic_progress_summary(db, owner_id: str, topic_id: str) -> dict:
    """
    Return aggregated completion stats for all lessons within a topic.

    Args:
        db: PyMongo database instance.
        owner_id: User or anonymous session identifier.
        topic_id: Topic identifier string.

    Returns:
        Dict with total, completed, in_progress, not_started counts.
    """
    pipeline = [
        {"$match": {"owner_id": owner_id, "topic_id": topic_id}},
        {
            "$group": {
                "_id": "$completion_status",
                "count": {"$sum": 1},
            }
        },
    ]
    results = list(db.progress.aggregate(pipeline))
    summary = {"total": 0, "completed": 0, "in_progress": 0, "not_started": 0}
    for r in results:
        status = r["_id"]
        count = r["count"]
        summary["total"] += count
        if status in summary:
            summary[status] = count
    return summary
