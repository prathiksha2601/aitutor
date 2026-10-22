"""
app/routes/topics.py
Routes for retrieving topics and educational lessons.
"""

from flask import Blueprint, request
from app.database import Database
from app.repositories import topics_repo, lessons_repo
from app.utils.responses import success_response, error_response, paginated_response
from app.utils.validators import validate_pagination

topics_bp = Blueprint("topics", __name__, url_prefix="/api")


@topics_bp.route("/topics", methods=["GET"])
def get_topics():
    db = Database.get_db()
    if db is None:
        return error_response("Database service is unavailable.", 503, "DB_UNAVAILABLE")

    page, per_page = validate_pagination(
        request.args.get("page", 1),
        request.args.get("per_page", 20),
    )

    topics = topics_repo.get_all_topics(db, page=page, per_page=per_page)
    total = topics_repo.count_topics(db)
    return paginated_response(topics, total, page, per_page)


@topics_bp.route("/lessons", methods=["GET"])
def get_lessons():
    db = Database.get_db()
    if db is None:
        return error_response("Database service is unavailable.", 503, "DB_UNAVAILABLE")

    topic_id = request.args.get("topic_id")
    page, per_page = validate_pagination(
        request.args.get("page", 1),
        request.args.get("per_page", 20),
    )

    if topic_id:
        lessons = lessons_repo.get_lessons_by_topic(db, topic_id, page=page, per_page=per_page)
        total = lessons_repo.count_lessons_by_topic(db, topic_id)
    else:
        lessons = lessons_repo.get_all_lessons(db, page=page, per_page=per_page)
        total = len(lessons)

    return paginated_response(lessons, total, page, per_page)


@topics_bp.route("/lessons/<lesson_id>", methods=["GET"])
def get_lesson(lesson_id: str):
    db = Database.get_db()
    if db is None:
        return error_response("Database service is unavailable.", 503, "DB_UNAVAILABLE")

    lesson = lessons_repo.get_lesson_by_id(db, lesson_id)
    if not lesson:
        return error_response("Lesson not found.", 404, "LESSON_NOT_FOUND")

    return success_response({"lesson": lesson})
