"""
app/repositories/users_repo.py
PyMongo repository for the users collection.
"""

from datetime import datetime, timezone
import logging
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)

_USER_PUBLIC_PROJECTION = {
    "_id": 1,
    "email": 1,
    "display_name": 1,
    "role": 1,
    "status": 1,
    "created_at": 1,
    "updated_at": 1,
}


def _serialize(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    if doc and "created_at" in doc and isinstance(doc["created_at"], datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    if doc and "updated_at" in doc and isinstance(doc["updated_at"], datetime):
        doc["updated_at"] = doc["updated_at"].isoformat()
    return doc


def create_user(db, user_data: dict) -> dict:
    now = datetime.now(timezone.utc)
    doc = {
        "email": user_data["email"].lower().strip(),
        "password_hash": user_data["password_hash"],
        "display_name": user_data.get("display_name", user_data["email"].split("@")[0]),
        "role": user_data.get("role", "student"),
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    result = db.users.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    doc.pop("password_hash", None)
    return _serialize(doc)


def get_user_by_email(db, email: str) -> dict | None:
    doc = db.users.find_one({"email": email.lower().strip()})
    return _serialize(doc) if doc else None


def get_user_by_id(db, user_id: str) -> dict | None:
    try:
        oid = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None
    doc = db.users.find_one({"_id": oid}, _USER_PUBLIC_PROJECTION)
    return _serialize(doc) if doc else None


def update_user(db, user_id: str, update_data: dict) -> dict | None:
    try:
        oid = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None
    allowed = {"display_name", "status"}
    filtered = {k: v for k, v in update_data.items() if k in allowed}
    if not filtered:
        return get_user_by_id(db, user_id)
    filtered["updated_at"] = datetime.now(timezone.utc)
    doc = db.users.find_one_and_update(
        {"_id": oid},
        {"$set": filtered},
        projection=_USER_PUBLIC_PROJECTION,
        return_document=True,
    )
    return _serialize(doc) if doc else None


def email_exists(db, email: str) -> bool:
    return db.users.count_documents({"email": email.lower().strip()}) > 0
