"""
app/routes/sessions.py
Learning sessions management: start, track video position, verify ownership, and end sessions.
"""

from flask import Blueprint, request
from app.database import Database
from app.repositories import sessions_repo
from app.security.auth import get_session_owner
from app.utils.responses import success_response, error_response
from app.schemas.session_schema import CreateSessionRequest, UpdateSessionRequest

sessions_bp = Blueprint("sessions", __name__, url_prefix="/api")


@sessions_bp.route("/sessions", methods=["POST"])
def create_session():
    db = Database.get_db()
    if db is None:
        return error_response("Database service unavailable.", 503, "DB_UNAVAILABLE")

    data = request.get_json(silent=True) or {}
    owner_id, is_auth = get_session_owner(request)

    lesson_id = data.get("lesson_id")
    topic_id = data.get("topic_id")
    if not lesson_id or not topic_id:
        return error_response("lesson_id and topic_id are required.", 400, "MISSING_FIELDS")

    session_data = {
        "user_id": owner_id,
        "topic_id": str(topic_id),
        "lesson_id": str(lesson_id),
        "is_authenticated": is_auth,
    }

    created = sessions_repo.create_session(db, session_data)
    return success_response({"session": created}, 201, "Learning session created.")


@sessions_bp.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id: str):
    db = Database.get_db()
    if db is None:
        return error_response("Database service unavailable.", 503, "DB_UNAVAILABLE")

    owner_id, _ = get_session_owner(request)
    session = sessions_repo.get_session_by_id(db, session_id)
    if not session:
        return error_response("Session not found.", 404, "SESSION_NOT_FOUND")

    # Enforce session ownership
    if session.get("user_id") != owner_id:
        return error_response("Forbidden: You do not own this session.", 403, "FORBIDDEN")

    return success_response({"session": session})


@sessions_bp.route("/sessions/<session_id>", methods=["PATCH"])
def update_session(session_id: str):
    db = Database.get_db()
    if db is None:
        return error_response("Database service unavailable.", 503, "DB_UNAVAILABLE")

    owner_id, _ = get_session_owner(request)
    if not sessions_repo.verify_session_ownership(db, session_id, owner_id):
        return error_response("Forbidden: You do not own this session.", 403, "FORBIDDEN")

    data = request.get_json(silent=True) or {}
    update_data = {}
    if "last_position_seconds" in data:
        try:
            pos = float(data["last_position_seconds"])
            if pos >= 0:
                update_data["last_position_seconds"] = pos
        except (ValueError, TypeError):
            return error_response("Invalid last_position_seconds.", 400, "INVALID_VALUE")

    if "status" in data and data["status"] in ("active", "completed", "paused"):
        update_data["status"] = data["status"]

    updated = sessions_repo.update_session(db, session_id, update_data)
    return success_response({"session": updated})


@sessions_bp.route("/sessions/<session_id>/end", methods=["POST"])
def end_session(session_id: str):
    db = Database.get_db()
    if db is None:
        return error_response("Database service unavailable.", 503, "DB_UNAVAILABLE")

    owner_id, _ = get_session_owner(request)
    if not sessions_repo.verify_session_ownership(db, session_id, owner_id):
        return error_response("Forbidden: You do not own this session.", 403, "FORBIDDEN")

    ended = sessions_repo.end_session(db, session_id)
    return success_response({"session": ended}, 200, "Session ended.")
