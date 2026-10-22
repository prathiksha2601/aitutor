"""
app/routes/progress.py
Learning progress tracking routes.
"""

from flask import Blueprint, request
from app.database import Database
from app.repositories import progress_repo
from app.security.auth import get_session_owner
from app.utils.responses import success_response, error_response

progress_bp = Blueprint("progress", __name__, url_prefix="/api")


@progress_bp.route("/progress", methods=["GET"])
def get_progress():
    db = Database.get_db()
    if db is None:
        return error_response("Database service unavailable.", 503, "DB_UNAVAILABLE")

    owner_id, _ = get_session_owner(request)
    records = progress_repo.get_progress_by_owner(db, owner_id)
    return success_response({"progress": records})


@progress_bp.route("/progress", methods=["POST"])
def update_progress():
    db = Database.get_db()
    if db is None:
        return error_response("Database service unavailable.", 503, "DB_UNAVAILABLE")

    owner_id, is_auth = get_session_owner(request)
    data = request.get_json(silent=True) or {}

    lesson_id = data.get("lesson_id")
    topic_id = data.get("topic_id")
    if not lesson_id or not topic_id:
        return error_response("lesson_id and topic_id are required.", 400, "MISSING_FIELDS")

    try:
        last_pos = float(data.get("last_position_seconds", 0))
    except (ValueError, TypeError):
        last_pos = 0.0

    status = data.get("completion_status", "in_progress")
    if status not in ("not_started", "in_progress", "completed"):
        status = "in_progress"

    progress_data = {
        "user_id": owner_id,
        "lesson_id": str(lesson_id),
        "topic_id": str(topic_id),
        "last_position_seconds": max(0.0, last_pos),
        "completion_status": status,
    }

    result = progress_repo.upsert_progress(db, progress_data)
    return success_response({"progress": result}, 200, "Progress recorded.")
