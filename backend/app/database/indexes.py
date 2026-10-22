"""
app/database/indexes.py
Creates all required MongoDB indexes for the EIT application.
Safe to call on every startup (idempotent).
"""

import logging
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)


def create_all_indexes(db) -> None:
    """
    Ensure all required indexes exist on every collection.

    Args:
        db: Active PyMongo database instance.
    """
    try:
        # ------------------------------------------------------------------
        # users – unique on email
        # ------------------------------------------------------------------
        db.users.create_index(
            [("email", ASCENDING)],
            unique=True,
            name="users_email_unique",
        )

        # ------------------------------------------------------------------
        # topics
        # ------------------------------------------------------------------
        db.topics.create_index(
            [("is_active", ASCENDING)],
            background=True,
            name="topics_is_active",
        )
        db.topics.create_index(
            [("category", ASCENDING)],
            background=True,
            name="topics_category",
        )

        # ------------------------------------------------------------------
        # lessons – compound: topic_id + is_published + sequence_number
        # ------------------------------------------------------------------
        db.lessons.create_index(
            [
                ("topic_id", ASCENDING),
                ("is_published", ASCENDING),
                ("sequence_number", ASCENDING),
            ],
            background=True,
            name="lessons_topic_published_seq",
        )

        # ------------------------------------------------------------------
        # learning_sessions
        # ------------------------------------------------------------------
        db.learning_sessions.create_index(
            [("user_id", ASCENDING)],
            background=True,
            name="sessions_user_id",
        )
        db.learning_sessions.create_index(
            [("lesson_id", ASCENDING)],
            background=True,
            name="sessions_lesson_id",
        )

        # ------------------------------------------------------------------
        # progress – unique compound: (user_id/anon_id, lesson_id, topic_id)
        # ------------------------------------------------------------------
        db.progress.create_index(
            [
                ("owner_id", ASCENDING),
                ("lesson_id", ASCENDING),
                ("topic_id", ASCENDING),
            ],
            unique=True,
            name="progress_owner_lesson_topic_unique",
        )

        # ------------------------------------------------------------------
        # conversations
        # ------------------------------------------------------------------
        db.conversations.create_index(
            [("session_id", ASCENDING)],
            background=True,
            name="conversations_session_id",
        )
        db.conversations.create_index(
            [("owner_id", ASCENDING)],
            background=True,
            name="conversations_owner_id",
        )

        # ------------------------------------------------------------------
        # quiz_attempts
        # ------------------------------------------------------------------
        db.quiz_attempts.create_index(
            [("session_id", ASCENDING)],
            background=True,
            name="quiz_attempts_session_id",
        )
        db.quiz_attempts.create_index(
            [("owner_id", ASCENDING)],
            background=True,
            name="quiz_attempts_owner_id",
        )

        # ------------------------------------------------------------------
        # expression_summaries – regular + TTL on expires_at
        # ------------------------------------------------------------------
        db.expression_summaries.create_index(
            [("session_id", ASCENDING)],
            background=True,
            name="expression_summaries_session_id",
        )
        db.expression_summaries.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
            background=True,
            name="expression_summaries_ttl",
        )

        # ------------------------------------------------------------------
        # audit_logs
        # ------------------------------------------------------------------
        db.audit_logs.create_index(
            [("actor_id", ASCENDING)],
            background=True,
            name="audit_logs_actor_id",
        )
        db.audit_logs.create_index(
            [("created_at", DESCENDING)],
            background=True,
            name="audit_logs_created_at",
        )

        logger.info("All MongoDB indexes created / verified successfully.")

    except OperationFailure as exc:
        logger.error("Failed to create MongoDB indexes: %s", exc)
        raise
