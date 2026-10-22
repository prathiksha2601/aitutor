"""
tests/backend/test_topics.py
Tests for topics and lessons retrieval endpoints.
"""


def test_get_topics_returns_list(client):
    res = client.get("/api/topics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0


def test_get_lessons_returns_list(client):
    res = client.get("/api/lessons")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_get_lesson_by_invalid_id_returns_404(client):
    res = client.get("/api/lessons/000000000000000000000000")
    assert res.status_code == 404
    data = res.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "LESSON_NOT_FOUND"


def test_get_lesson_by_valid_id(client):
    # Fetch first available lesson
    lessons_res = client.get("/api/lessons")
    lessons = lessons_res.get_json()["data"]
    if lessons:
        first_id = lessons[0]["_id"]
        res = client.get(f"/api/lessons/{first_id}")
        assert res.status_code == 200
        assert res.get_json()["data"]["lesson"]["_id"] == first_id
