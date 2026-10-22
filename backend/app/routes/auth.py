"""
app/routes/auth.py
Authentication blueprint for user registration, login, logout, and current user profile.
"""

from flask import Blueprint, request
from app.database import Database
from app.repositories import users_repo
from app.security.auth import (
    hash_password,
    verify_password,
    generate_token,
    get_current_user_id,
    require_auth,
)
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_email, sanitize_string

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    display_name = sanitize_string(data.get("display_name", ""))

    if not validate_email(email):
        return error_response("A valid email address is required.", 400, "INVALID_EMAIL")

    if not password or len(password) < 8:
        return error_response("Password must be at least 8 characters long.", 400, "WEAK_PASSWORD")

    db = Database.get_db()
    if db is None:
        return error_response("Database service unavailable.", 503, "DB_UNAVAILABLE")

    if users_repo.email_exists(db, email):
        return error_response("An account with this email already exists.", 409, "EMAIL_EXISTS")

    pwd_hash = hash_password(password)
    user_data = {
        "email": email,
        "password_hash": pwd_hash,
        "display_name": display_name or email.split("@")[0],
        "role": "student",
    }
    created_user = users_repo.create_user(db, user_data)
    token = generate_token(created_user["_id"], role=created_user["role"])

    return success_response({
        "token": token,
        "user": created_user,
    }, 201, "Account registered successfully.")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return error_response("Email and password are required.", 400, "MISSING_CREDENTIALS")

    db = Database.get_db()
    if db is None:
        return error_response("Database service unavailable.", 503, "DB_UNAVAILABLE")

    user = users_repo.get_user_by_email(db, email)
    if not user or not verify_password(password, user.get("password_hash", "")):
        return error_response("Invalid email or password.", 401, "INVALID_CREDENTIALS")

    user_id = user["_id"]
    token = generate_token(user_id, role=user.get("role", "student"))

    user_profile = {
        "_id": user_id,
        "email": user["email"],
        "display_name": user.get("display_name"),
        "role": user.get("role", "student"),
        "created_at": user.get("created_at"),
    }

    return success_response({
        "token": token,
        "user": user_profile,
    }, 200, "Login successful.")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    return success_response({}, 200, "Logged out successfully.")


@auth_bp.route("/me", methods=["GET"])
@require_auth
def get_me():
    user_id = get_current_user_id()
    db = Database.get_db()
    if db is None:
        return error_response("Database unavailable.", 503, "DB_UNAVAILABLE")

    user = users_repo.get_user_by_id(db, user_id)
    if not user:
        return error_response("User not found.", 404, "USER_NOT_FOUND")

    return success_response({"user": user})
