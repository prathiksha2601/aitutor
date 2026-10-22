"""
app/security/auth.py
Authentication and authorization utilities: Argon2id hashing & JWT tokens.
"""

from datetime import datetime, timezone, timedelta
from functools import wraps
import logging
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from flask import request, jsonify, current_app

from app.config import config

logger = logging.getLogger(__name__)

# Argon2id password hasher
_ph = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)


def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return _ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against Argon2id hash."""
    try:
        return _ph.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, Exception):
        return False


def generate_token(user_id: str, role: str = "student") -> str:
    """Generate a JWT token valid for SESSION_TIMEOUT_HOURS."""
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(hours=config.SESSION_TIMEOUT_HOURS)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expiry.timestamp()),
    }
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict | None:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_current_user_id(req=None) -> str | None:
    """Extract authenticated user_id from Authorization Bearer header."""
    r = req or request
    auth_header = r.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        payload = verify_token(token)
        if payload and "sub" in payload:
            return payload["sub"]
    return None


def get_session_owner(req=None) -> tuple[str, bool]:
    """
    Return (owner_id, is_authenticated).
    Checks Authorization Bearer JWT first.
    Falls back to X-Session-ID header for anonymous sessions.
    Falls back to a default anonymous-fallback if neither provided.
    """
    user_id = get_current_user_id(req)
    if user_id:
        return user_id, True

    r = req or request
    anon_session_id = r.headers.get("X-Session-ID")
    if anon_session_id:
        return anon_session_id.strip(), False

    # Also check JSON body if available
    try:
        body = r.get_json(silent=True) or {}
        if "anonymous_session_id" in body and body["anonymous_session_id"]:
            return body["anonymous_session_id"].strip(), False
        if "session_id" in body and body["session_id"]:
            return body["session_id"].strip(), False
    except Exception:
        pass

    return "anonymous_guest", False


def require_auth(f):
    """Decorator requiring valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({
                "success": False,
                "error": {"message": "Authentication required", "code": "UNAUTHORIZED"}
            }), 401
        return f(*args, **kwargs)
    return decorated
