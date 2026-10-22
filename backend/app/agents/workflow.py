"""
app/agents/workflow.py
Controlled 7-step EIT Learning Agent workflow.
"""

from datetime import datetime, timezone
import logging
from typing import Any

from app.agents.state import AgentState
from app.agents.policies import (
    validate_agent_request,
    sanitize_expression_context,
)
from app.agents.tools import (
    get_lesson_tool,
    get_topic_tool,
    get_conversation_tool,
    get_progress_tool,
)
from app.tutoring.tutor_service import TutorService
from app.repositories import conversations_repo

logger = logging.getLogger(__name__)


class EITLearningAgent:
    """
    Controlled 7-step EIT Learning Agent.
    Strictly forbids arbitrary code execution and restricts data retrieval to approved tools.
    """

    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.tutor_service = TutorService(config)

    def run(self, state: AgentState) -> AgentState:
        """Execute the 7-step workflow."""
        try:
            # Step 1: Request understanding & validation
            self._step_1_understand(state)

            # Step 2: Context retrieval via allowlisted tools
            self._step_2_retrieve_context(state)

            # Step 3: Learning-support analysis
            self._step_3_analyze_support(state)

            # Step 4: Tutor response generation
            self._step_4_generate_response(state)

            # Step 5: Verification of response structure
            self._step_5_verify_response(state)

            # Step 6: Persistence to MongoDB
            self._step_6_persist(state)

            # Step 7: Finalise response metadata
            self._step_7_finalize(state)

        except Exception as exc:
            logger.error("EIT Learning Agent workflow error: %s", exc)
            state.error = str(exc)
            if not state.tutor_response:
                state.tutor_response = (
                    "I ran into an unexpected issue preparing this response. "
                    "Please try again in a moment."
                )

        return state

    def _step_1_understand(self, state: AgentState) -> None:
        """Validate request against policy allowlists."""
        validate_agent_request(state.request_type, state.response_mode)

    def _step_2_retrieve_context(self, state: AgentState) -> None:
        """Retrieve context using approved tools only."""
        if state.lesson_id:
            state.lesson_data = get_lesson_tool(self.db, state.lesson_id)
            if state.lesson_data and not state.topic_id:
                state.topic_id = state.lesson_data.get("topic_id")

        if state.topic_id:
            state.topic_data = get_topic_tool(self.db, state.topic_id)

        if state.session_id:
            state.recent_messages = get_conversation_tool(self.db, state.session_id, limit=6)

        if state.owner_id and state.lesson_id:
            state.progress_data = get_progress_tool(self.db, state.owner_id, state.lesson_id)

    def _step_3_analyze_support(self, state: AgentState) -> None:
        """Sanitize any expression signal to ensure it remains an uncertain, secondary cue."""
        if state.expression_context:
            state.expression_context = sanitize_expression_context(state.expression_context)

    def _step_4_generate_response(self, state: AgentState) -> None:
        """Generate tutor response using OpenAI service."""
        response_text = self.tutor_service.generate_response(state)
        state.tutor_response = response_text

    def _step_5_verify_response(self, state: AgentState) -> None:
        """Ensure response is non-empty and well-formed."""
        if not state.tutor_response or not state.tutor_response.strip():
            state.tutor_response = "I'm ready to help you with this topic! What questions do you have?"

    def _step_6_persist(self, state: AgentState) -> None:
        """Persist message exchange in conversation repository if session exists."""
        if self.db is None or not state.session_id:
            return
        try:
            now = datetime.now(timezone.utc).isoformat()
            user_msg = {
                "role": "user",
                "content": state.student_message,
                "created_at": now,
            }
            assistant_msg = {
                "role": "assistant",
                "content": state.tutor_response,
                "response_mode": state.response_mode,
                "created_at": now,
            }
            # Append user message
            conversations_repo.append_message(self.db, state.session_id, user_msg)
            # Append assistant response
            conversations_repo.append_message(self.db, state.session_id, assistant_msg)
        except Exception as exc:
            logger.warning("Failed to persist conversation: %s", exc)

    def _step_7_finalize(self, state: AgentState) -> None:
        """Add metadata for response."""
        state.response_metadata = {
            "response_mode": state.response_mode,
            "request_type": state.request_type,
            "ai_configured": self.tutor_service.is_available(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
