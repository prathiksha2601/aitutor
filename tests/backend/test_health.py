"""
tests/backend/test_health.py
Tests for GET /api/health endpoint.
"""

from unittest.mock import patch


def test_health_endpoint_returns_200(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["status"] == "ok"
    assert data["data"]["version"] == "1.0.0"


def test_health_reports_db_connectivity(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "db_connected" in data
    assert isinstance(data["db_connected"], bool)


def test_health_reports_service_configuration(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    services = res.get_json()["data"]["services"]
    assert "model_configured" in services
    assert "openai_configured" in services
