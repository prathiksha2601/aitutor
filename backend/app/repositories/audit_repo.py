"""
app/repositories/audit_repo.py
PyMongo repository for the audit_logs collection.
"""

from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def log_action(
    db,
    actor_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    outcome: str = "success",
    request_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    """Record an audit log entry. Never raises exceptions."""
    try:
        if db is None:
            return
        doc = {
            "actor_id": actor_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "outcome": outcome,
            "request_id": request_id,
            "created_at": datetime.now(timezone.utc),
            "metadata": metadata or {},
        }
        db.audit_logs.insert_one(doc)
    except Exception as exc:
        logger.warning("Failed to record audit log: %s", exc)
