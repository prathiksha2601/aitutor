"""
tests/backend/conftest.py
Pytest fixtures for backend testing with test client and mocked DB / OpenAI.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

# Ensure backend directory is in python path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app import create_app
from app.config import Config


class TestConfig(Config):
    FLASK_ENV = "testing"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"
    MONGODB_DATABASE = "eit_database"
    RATE_LIMIT_PER_MINUTE = 1000
    OPENAI_API_KEY = None


@pytest.fixture(scope="session")
def app():
    test_cfg = TestConfig()
    app = create_app(test_cfg)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_openai():
    with patch("openai.OpenAI") as mock:
        yield mock
