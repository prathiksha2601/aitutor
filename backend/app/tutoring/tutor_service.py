"""
app/tutoring/tutor_service.py
AI Tutor service interacting with OpenAI SDK.
Includes system prompts for various pedagogical modes and graceful fallbacks.
"""

import logging
from typing import Any

from app.config import Config, config as default_config
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

MODE_INSTRUCTIONS = {
    "simple": "Explain this concept in simple, beginner-friendly terms. Avoid heavy jargon.",
    "step_by_step": "Provide a clear, numbered step-by-step walkthrough of this concept.",
    "example": "Give an intuitive, real-world analogy and practical example to illustrate this concept.",
    "programming": "Provide a clean, well-commented code example illustrating this concept, followed by an explanation.",
    "quiz": "Generate an interactive practice question with 4 multiple choice options (A, B, C, D). Do not reveal the answer immediately.",
    "feedback": "Evaluate the student's submitted answer warmly and constructively. Highlight what is correct, gently explain any misconceptions, and provide the model answer.",
    "summary": "Summarize the key takeaways of this lesson in 3 to 5 concise bullet points.",
    "revision": "Provide 3 concise revision questions to test understanding of the main concepts.",
}

UNAVAILABLE_MESSAGE = (
    "The AI tutor is not currently configured. "
    "To enable interactive tutoring, please add your OPENAI_API_KEY in the backend .env file."
)


class TutorService:
    """Encapsulates OpenAI LLM communication with bounded retries and timeouts."""

    def __init__(self, cfg: Config | None = None):
        self.config = cfg or default_config
        self.client = None
        self._init_client()

    def _init_client(self) -> None:
        if self.config.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.config.OPENAI_API_KEY,
                    timeout=30.0,
                    max_retries=2,
                )
                logger.info("OpenAI client initialised successfully with model %s", self.config.OPENAI_MODEL)
            except Exception as exc:
                logger.warning("Failed to initialize OpenAI client: %s", exc)
                self.client = None
        else:
            logger.info("OPENAI_API_KEY not configured. Tutor service will return setup instructions.")

    def is_available(self) -> bool:
        return self.client is not None

    def build_system_prompt(self, state: AgentState) -> str:
        mode_instruction = MODE_INSTRUCTIONS.get(state.response_mode, MODE_INSTRUCTIONS["simple"])
        system_prompt = (
            "You are the AI-Driven Emotional Intelligence Tutor (EIT), a supportive, encouraging, "
            "and pedagogically sound computer science and programming tutor.\n\n"
            f"Instruction Mode: {state.response_mode.upper()}\n"
            f"{mode_instruction}\n\n"
            "Guidelines:\n"
            "- Speak directly to the student in an encouraging, engaging tone.\n"
            "- Never claim you can read the student's mind or emotions.\n"
            "- Keep answers focused on the learning objective.\n"
            "- Use Markdown for code blocks and formatting.\n"
        )

        if state.topic_data:
            system_prompt += f"\nCurrent Topic: {state.topic_data.get('title')} - {state.topic_data.get('description', '')}"

        if state.lesson_data:
            system_prompt += f"\nCurrent Lesson: {state.lesson_data.get('title')} - {state.lesson_data.get('description', '')}"

        if state.expression_context and state.expression_context.get("suggested_support"):
            support = state.expression_context["suggested_support"]
            system_prompt += (
                f"\nPedagogical note (uncertain signal): The student may benefit from {support}. "
                "Naturally offer this support without mentioning facial analysis."
            )

        return system_prompt

    def build_messages(self, state: AgentState) -> list[dict]:
        messages = [{"role": "system", "content": self.build_system_prompt(state)}]

        # Add recent conversation history (up to 6 past messages)
        for msg in state.recent_messages[-6:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

        # Add current user prompt
        messages.append({"role": "user", "content": state.student_message})
        return messages

    def generate_response(self, state: AgentState) -> str:
        """Call OpenAI chat completion API or return fallback."""
        if not self.is_available():
            return UNAVAILABLE_MESSAGE

        try:
            messages = self.build_messages(state)
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            content = response.choices[0].message.content
            return content.strip() if content else "I'm here to help! Could you please clarify your question?"
        except Exception as exc:
            logger.error("OpenAI generation failed: %s", exc)
            err_str = str(exc)
            if "insufficient_quota" in err_str or "credit_balance_exhausted" in err_str:
                return (
                    "OpenAI API key connected, but the account has no remaining credits (quota exhausted). "
                    "Please add billing credits at https://platform.openai.com/settings/organization/billing."
                )
            return (
                "I encountered an error connecting to the AI service. "
                "Please verify your network connection and API key configuration."
            )
