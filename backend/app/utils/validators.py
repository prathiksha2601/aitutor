"""
app/utils/validators.py
Input validation utilities used across routes and services.
"""

import re
from bson import ObjectId
from bson.errors import InvalidId


def validate_object_id(id_str: str) -> ObjectId:
    """
    Convert a string to a BSON ObjectId.

    Args:
        id_str: Hex string representation of an ObjectId.

    Returns:
        Valid ObjectId instance.

    Raises:
        ValueError: If the string is not a valid ObjectId.
    """
    if not id_str or not isinstance(id_str, str):
        raise ValueError("ID must be a non-empty string.")
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise ValueError(f"'{id_str}' is not a valid resource ID.")


def sanitize_string(s: str, max_length: int = 1000) -> str:
    """
    Strip surrounding whitespace and truncate to max_length.

    Args:
        s: Input string.
        max_length: Maximum allowed character count.

    Returns:
        Sanitised string.
    """
    if not isinstance(s, str):
        return ""
    return s.strip()[:max_length]


def validate_email(email: str) -> bool:
    """
    Basic RFC-5322-inspired email format check.

    Args:
        email: Email address string.

    Returns:
        True if the format looks valid.
    """
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_pagination(
    page,
    per_page,
    max_per_page: int = 50,
) -> tuple[int, int]:
    """
    Normalise and clamp pagination parameters.

    Args:
        page: Requested page number (1-indexed).
        per_page: Items per page.
        max_per_page: Upper bound on per_page.

    Returns:
        Tuple of (page, per_page) as valid integers.
    """
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 20

    page = max(1, page)
    per_page = max(1, min(per_page, max_per_page))
    return page, per_page
