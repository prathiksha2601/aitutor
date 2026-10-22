"""
app/config.py
Configuration class for the EIT Flask backend.
Reads all settings from environment variables via python-dotenv.
"""

import os
from dotenv import load_dotenv

# Load .env file at module level so all subsequent os.getenv calls see the values
load_dotenv()


class Config:
    """Central configuration object built from environment variables."""

    # Flask
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "eit_database")

    # OpenAI
    _raw_openai_key: str | None = os.getenv("OPENAI_API_KEY") or None
    OPENAI_API_KEY: str | None = _raw_openai_key if _raw_openai_key else None
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # CORS
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # ML model paths
    MODEL_PATH: str = os.getenv("MODEL_PATH", "../ml/artifacts/expression_model.keras")
    MODEL_LABELS_PATH: str = os.getenv("MODEL_LABELS_PATH", "../ml/artifacts/labels.json")

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")

    # Session / conversation settings
    SESSION_TIMEOUT_HOURS: int = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
    MAX_CONVERSATION_MESSAGES: int = int(os.getenv("MAX_CONVERSATION_MESSAGES", "50"))

    # Expression analysis
    EXPRESSION_AGGREGATION_WINDOW: int = int(os.getenv("EXPRESSION_AGGREGATION_WINDOW", "10"))

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    @property
    def DEBUG(self) -> bool:
        """Return True only when running in development mode."""
        return self.FLASK_ENV == "development"


# Singleton instance used across the application
config = Config()
