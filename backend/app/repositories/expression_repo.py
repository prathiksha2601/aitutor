"""
app/repositories/expression_repo.py
PyMongo repository for expression_summaries collection.
Only used when consent is explicitly granted.
"""

from datetime import datetime, timezone, timedelta
import logging
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)


def _serialize(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    for dt_field in ("created_at", "observation_window_start", "observation_window_end", "expires_at"):
        if doc and dt_field in doc and isinstance(doc[dt_field], datetime):
            doc[dt_field] = doc[dt_field].isoformat()
    return doc


def create_expression_summary(db, summary_data: dict) -> dict | None:
    """Insert aggregated expression summary. Only called when consent=True."""
    if not summary_data.get("consent"):
        logger.warning("Attempted to persist expression summary without consent")
        return None
    now = datetime.now(timezone.utc)
    doc = {
        "session_id": summary_data["session_id"],
        "owner_id": summary_data.get("owner_id"),
        "observation_window_start": summary_data.get("observation_window_start", now),
        "observation_window_end": summary_data.get("observation_window_end", now),
        "aggregated_category_counts": summary_data.get("aggregated_category_counts", {}),
        "quality_metadata": summary_data.get("quality_metadata", {}),
        "model_version": summary_data.get("model_version", "1.0.0"),
        "created_at": now,
        "expires_at": now + timedelta(days=7),
    }
    result = db.expression_summaries.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return _serialize(doc)


def get_summaries_by_session(db, session_id: str, owner_id: str) -> list[dict]:
    query = {"session_id": session_id, "owner_id": owner_id}
    cursor = db.expression_summaries.find(query).sort("created_at", -1).limit(50)
    return [_serialize(doc) for doc in cursor]
