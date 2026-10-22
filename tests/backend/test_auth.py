"""
tests/backend/test_auth.py
Tests for authentication: register, login, logout, and protected endpoints.
"""


def test_register_weak_password_rejected(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "student1@example.com", "password": "short"},
    )
    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "WEAK_PASSWORD"


def test_register_and_login_success(client):
    test_email = "alice_test@example.com"
    test_pass = "SecureP@ssw0rd123"

    # Register
    reg_res = client.post(
        "/api/auth/register",
        json={"email": test_email, "password": test_pass, "display_name": "Alice"},
    )
    assert reg_res.status_code in (201, 409)  # 409 if run repeatedly on same DB

    # Login
    login_res = client.post(
        "/api/auth/login",
        json={"email": test_email, "password": test_pass},
    )
    assert login_res.status_code == 200
    token = login_res.get_json()["data"]["token"]
    assert token is not None

    # Access protected /api/auth/me
    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.get_json()["data"]["user"]["email"] == test_email


def test_protected_me_without_token_returns_401(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    assert res.get_json()["error"]["code"] == "UNAUTHORIZED"
