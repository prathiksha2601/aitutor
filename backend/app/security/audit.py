"""
app/security/audit.py
Security audit helper.
"""

from app.database import Database
from app.repositories import audit_repo


def record_action(
    actor_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    outcome: str = "success",
    request_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    """Safely log an audit action without ever raising."""
    db = Database.get_db()
    audit_repo.log_action(
        db,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        request_id=request_id,
        metadata=metadata,
    )
