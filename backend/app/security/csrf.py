"""
app/security/csrf.py
CSRF token generation and validation.
"""

import hmac
import secrets


def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token."""
    return secrets.token_hex(32)


def validate_csrf_token(request_token: str | None, session_token: str | None) -> bool:
    """Validate CSRF token using constant-time comparison."""
    if not request_token or not session_token:
        return False
    return hmac.compare_digest(request_token, session_token)
