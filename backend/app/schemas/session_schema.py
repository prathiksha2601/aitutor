"""
app/schemas/session_schema.py
Pydantic request models for session and progress endpoints.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """Payload for POST /api/sessions."""

    lesson_id: str
    topic_id: str
    anonymous_session_id: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    """Payload for PATCH /api/sessions/<id>."""

    last_position_seconds: Optional[float] = Field(default=None, ge=0)
    status: Optional[Literal["active", "completed", "paused"]] = None


class CreateProgressRequest(BaseModel):
    """Payload for POST /api/progress."""

    lesson_id: str
    topic_id: str
    last_position_seconds: float = Field(ge=0)
    completion_status: Literal["not_started", "in_progress", "completed"]
