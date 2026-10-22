"""
app/utils/responses.py
Standardised JSON response helpers used by all route handlers.
"""

from flask import jsonify


def success_response(data=None, status: int = 200, message: str | None = None):
    """
    Build a successful JSON response.

    Args:
        data: Response payload (dict, list, or None).
        status: HTTP status code (default 200).
        message: Optional human-readable message.

    Returns:
        (Response, status) tuple compatible with Flask return values.
    """
    body = {
        "success": True,
        "data": data,
    }
    if message is not None:
        body["message"] = message
    return jsonify(body), status


def error_response(message: str, status: int = 400, code: str | None = None):
    """
    Build an error JSON response.

    Args:
        message: Human-readable error description.
        status: HTTP status code (default 400).
        code: Optional machine-readable error code string.

    Returns:
        (Response, status) tuple compatible with Flask return values.
    """
    body = {
        "success": False,
        "error": {
            "message": message,
            "code": code,
        },
    }
    return jsonify(body), status


def paginated_response(
    items: list,
    total: int,
    page: int,
    per_page: int,
    status: int = 200,
):
    """
    Build a paginated JSON response with metadata.

    Args:
        items: Page of result items.
        total: Total item count across all pages.
        page: Current page number (1-indexed).
        per_page: Items per page.
        status: HTTP status code (default 200).

    Returns:
        (Response, status) tuple compatible with Flask return values.
    """
    import math

    total_pages = math.ceil(total / per_page) if per_page else 1
    body = {
        "success": True,
        "data": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }
    return jsonify(body), status
