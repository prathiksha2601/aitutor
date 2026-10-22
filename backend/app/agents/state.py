"""
app/agents/state.py
Typed state dataclass for the EIT Learning Agent workflow.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    session_id: str
    owner_id: str
    student_message: str
    request_type: str = "chat"          # chat | explain | quiz | feedback | summary | revision
    response_mode: str = "simple"       # simple | step_by_step | example | programming | quiz | feedback | summary | revision
    topic_id: str | None = None
    lesson_id: str | None = None
    lesson_data: dict | None = None
    topic_data: dict | None = None
    recent_messages: list[dict] = field(default_factory=list)
    progress_data: dict | None = None
    expression_context: dict | None = None  # Always treated as uncertain, optional signal
    tutor_response: str | None = None
    response_metadata: dict = field(default_factory=dict)
    error: str | None = None
    retries: int = 0
