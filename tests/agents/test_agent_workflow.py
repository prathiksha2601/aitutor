"""
tests/agents/test_agent_workflow.py
Tests for the 7-step EIT Learning Agent workflow.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from app.agents.state import AgentState
from app.agents.workflow import EITLearningAgent
from app.config import Config


def test_agent_workflow_graceful_fallback_when_openai_missing():
    cfg = Config()
    cfg.OPENAI_API_KEY = None

    agent = EITLearningAgent(db=None, config=cfg)
    state = AgentState(
        session_id="test_session_abc",
        owner_id="test_student",
        student_message="Explain what a binary tree is.",
        request_type="chat",
        response_mode="simple",
    )

    result = agent.run(state)
    assert result.tutor_response is not None
    assert "OPENAI_API_KEY" in result.tutor_response or "not currently configured" in result.tutor_response
    assert result.response_metadata["response_mode"] == "simple"
    assert result.response_metadata["ai_configured"] is False


def test_agent_workflow_with_mocked_openai():
    cfg = Config()
    cfg.OPENAI_API_KEY = "sk-mock-key"

    mock_choice = MagicMock()
    mock_choice.message.content = "A binary tree is a hierarchical data structure."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("openai.OpenAI") as mock_openai_cls:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_instance

        agent = EITLearningAgent(db=None, config=cfg)
        state = AgentState(
            session_id="test_session_xyz",
            owner_id="test_student",
            student_message="What is a tree?",
            request_type="explain",
            response_mode="step_by_step",
        )

        result = agent.run(state)
        assert result.tutor_response == "A binary tree is a hierarchical data structure."
        assert result.response_metadata["response_mode"] == "step_by_step"
