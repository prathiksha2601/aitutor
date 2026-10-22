"""
tests/backend/test_tutor.py
Tests for AI tutor chat, explanation, quiz, and feedback endpoints.
"""

from unittest.mock import patch, MagicMock


def test_tutor_chat_missing_session_id(client):
    res = client.post(
        "/api/tutor/chat",
        json={"message": "What is encapsulation?"},
    )
    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "MISSING_SESSION_ID"


def test_tutor_chat_empty_message(client):
    res = client.post(
        "/api/tutor/chat",
        json={"message": "", "session_id": "test_sess_1"},
    )
    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "EMPTY_MESSAGE"


def test_tutor_chat_missing_api_key_returns_setup_message(client):
    """When OPENAI_API_KEY is not configured, returns clear setup instructions."""
    res = client.post(
        "/api/tutor/chat",
        json={"message": "Can you explain loops?", "session_id": "test_sess_2"},
        headers={"X-Session-ID": "test_user"},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "OPENAI_API_KEY" in data["response"] or "not currently configured" in data["response"]


def test_tutor_chat_with_mocked_openai(client):
    mock_choice = MagicMock()
    mock_choice.message.content = "Encapsulation is the bundling of data and methods that operate on that data."

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    with patch("openai.OpenAI") as mock_openai_cls:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = mock_completion
        mock_openai_cls.return_value = mock_instance

        # Temporarily enable client with mock
        with patch.object(client.application.config["EIT_CONFIG"], "OPENAI_API_KEY", "sk-mock-key"):
            res = client.post(
                "/api/tutor/chat",
                json={
                    "message": "What is encapsulation?",
                    "session_id": "test_sess_3",
                    "response_mode": "simple",
                },
                headers={"X-Session-ID": "test_user"},
            )
            assert res.status_code == 200
            assert "Encapsulation" in res.get_json()["data"]["response"]


def test_tutor_feedback_saves_quiz_attempt(client):
    res = client.post(
        "/api/tutor/feedback",
        json={
            "session_id": "test_sess_4",
            "question": "What is the time complexity of binary search?",
            "submitted_answer": "O(log n)",
        },
        headers={"X-Session-ID": "test_user"},
    )
    assert res.status_code == 200
    assert "feedback" in res.get_json()["data"]
