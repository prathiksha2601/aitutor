"""
tests/backend/test_expression.py
Tests for expression analysis and session signals persistence.
"""

import base64


def test_analyze_without_consent_returns_403(client):
    """CRITICAL PRIVACY TEST: Server refuses processing without consent."""
    res = client.post(
        "/api/expression/analyze",
        json={"image_b64": "dummy_data", "consent": False},
    )
    assert res.status_code == 403
    assert res.get_json()["error"]["code"] == "CONSENT_REQUIRED"


def test_analyze_missing_image_returns_400(client):
    res = client.post(
        "/api/expression/analyze",
        json={"consent": True},
    )
    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "MISSING_IMAGE"


def test_analyze_with_consent_reports_status(client):
    # 1x1 black pixel JPEG base64
    tiny_jpeg_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="

    res = client.post(
        "/api/expression/analyze",
        json={"image_b64": tiny_jpeg_b64, "consent": True},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "expression" in data
    # When model is not yet trained, status must be 'unavailable' (never fake numbers)
    assert data["expression"]["status"] in ("ok", "unavailable")
    assert "uncertain_signal_notice" in data
