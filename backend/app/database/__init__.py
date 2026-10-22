"""
app/database/__init__.py
MongoDB connection management with singleton pattern.
"""

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class Database:
    """Manages a single MongoClient connection for the application lifetime."""

    _client: MongoClient | None = None
    _db = None

    @classmethod
    def connect(cls, uri: str, db_name: str) -> None:
        """
        Create a MongoClient and pin the target database.

        Args:
            uri: MongoDB connection URI.
            db_name: Name of the database to use.

        Raises:
            ConnectionFailure: If the server cannot be reached on startup.
        """
        try:
            cls._client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            cls._db = cls._client[db_name]
            # Eagerly verify connectivity
            cls._client.admin.command("ping")
            logger.info("MongoDB connected: database=%s", db_name)
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            logger.error("MongoDB connection failed: %s", exc)
            raise

    @classmethod
    def get_db(cls):
        """Return the active database instance."""
        return cls._db

    @classmethod
    def health_check(cls) -> bool:
        """
        Ping the MongoDB server.

        Returns:
            True if the server responds, False otherwise.
        """
        if cls._client is None:
            return False
        try:
            cls._client.admin.command("ping")
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("MongoDB health-check failed: %s", exc)
            return False

    @classmethod
    def close(cls) -> None:
        """Close the MongoClient connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("MongoDB connection closed.")


# Module-level singleton reference kept for convenience
db_instance: Database = Database


def get_database():
    """Return the active MongoDB database object."""
    return Database.get_db()
