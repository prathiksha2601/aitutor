"""
tests/backend/test_sessions.py
Tests for sessions routes and ownership verification.
"""


def test_create_session(client):
    res = client.post(
        "/api/sessions",
        json={"lesson_id": "test_lesson_1", "topic_id": "test_topic_1"},
        headers={"X-Session-ID": "test-student-alice"},
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["session"]["user_id"] == "test-student-alice"


def test_get_own_session(client):
    create_res = client.post(
        "/api/sessions",
        json={"lesson_id": "test_lesson_2", "topic_id": "test_topic_1"},
        headers={"X-Session-ID": "test-student-alice"},
    )
    session_id = create_res.get_json()["data"]["session"]["_id"]

    res = client.get(
        f"/api/sessions/{session_id}",
        headers={"X-Session-ID": "test-student-alice"},
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["session"]["_id"] == session_id


def test_get_session_other_owner_returns_403(client):
    """CRITICAL SECURITY TEST: Ensure a user cannot access another student's session."""
    create_res = client.post(
        "/api/sessions",
        json={"lesson_id": "test_lesson_3", "topic_id": "test_topic_1"},
        headers={"X-Session-ID": "legitimate-student"},
    )
    session_id = create_res.get_json()["data"]["session"]["_id"]

    # Attempt to access using a different student's identity
    res = client.get(
        f"/api/sessions/{session_id}",
        headers={"X-Session-ID": "malicious-actor"},
    )
    assert res.status_code == 403
    assert res.get_json()["error"]["code"] == "FORBIDDEN"


def test_update_session_position(client):
    create_res = client.post(
        "/api/sessions",
        json={"lesson_id": "test_lesson_4", "topic_id": "test_topic_1"},
        headers={"X-Session-ID": "test-student-alice"},
    )
    session_id = create_res.get_json()["data"]["session"]["_id"]

    res = client.patch(
        f"/api/sessions/{session_id}",
        json={"last_position_seconds": 120.5},
        headers={"X-Session-ID": "test-student-alice"},
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["session"]["last_position_seconds"] == 120.5


def test_end_session(client):
    create_res = client.post(
        "/api/sessions",
        json={"lesson_id": "test_lesson_5", "topic_id": "test_topic_1"},
        headers={"X-Session-ID": "test-student-alice"},
    )
    session_id = create_res.get_json()["data"]["session"]["_id"]

    res = client.post(
        f"/api/sessions/{session_id}/end",
        headers={"X-Session-ID": "test-student-alice"},
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["session"]["status"] == "completed"
