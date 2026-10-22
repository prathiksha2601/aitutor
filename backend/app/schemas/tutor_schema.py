"""
app/schemas/tutor_schema.py
Pydantic request models for AI tutor endpoints.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Payload for POST /api/tutor/chat."""

    session_id: str
    message: str = Field(max_length=2000)
    topic_id: Optional[str] = None
    lesson_id: Optional[str] = None
    response_mode: Literal[
        "simple",
        "step_by_step",
        "example",
        "programming",
        "quiz",
        "feedback",
        "summary",
        "revision",
    ] = "simple"


class QuizRequest(BaseModel):
    """Payload for POST /api/tutor/quiz."""

    session_id: str
    topic_id: str
    lesson_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    """Payload for POST /api/tutor/feedback."""

    session_id: str
    question: str
    submitted_answer: str = Field(max_length=2000)
    topic_id: str
    lesson_id: Optional[str] = None
