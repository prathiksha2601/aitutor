"""
app/routes/tutor.py
AI Tutor endpoints: chat, explain, quiz, and answer feedback.
Executes the controlled 7-step EIT Learning Agent workflow.
"""

from flask import Blueprint, request, current_app
from app.database import Database
from app.config import config
from app.security.auth import get_session_owner
from app.agents.state import AgentState
from app.agents.workflow import EITLearningAgent
from app.repositories import quiz_repo
from app.utils.responses import success_response, error_response
from app.utils.validators import sanitize_string

tutor_bp = Blueprint("tutor", __name__, url_prefix="/api/tutor")


@tutor_bp.route("/chat", methods=["POST"])
def tutor_chat():
    data = request.get_json(silent=True) or {}
    message = sanitize_string(data.get("message", ""), max_length=2000)
    session_id = data.get("session_id")

    if not message:
        return error_response("Message cannot be empty.", 400, "EMPTY_MESSAGE")
    if not session_id:
        return error_response("session_id is required.", 400, "MISSING_SESSION_ID")

    owner_id, _ = get_session_owner(request)
    db = Database.get_db()

    response_mode = data.get("response_mode", "simple")
    if response_mode not in (
        "simple", "step_by_step", "example", "programming",
        "quiz", "feedback", "summary", "revision"
    ):
        response_mode = "simple"

    state = AgentState(
        session_id=str(session_id),
        owner_id=owner_id,
        student_message=message,
        request_type="chat",
        response_mode=response_mode,
        topic_id=data.get("topic_id"),
        lesson_id=data.get("lesson_id"),
        expression_context=data.get("expression_context"),
    )

    cfg = current_app.config.get("EIT_CONFIG", config)
    agent = EITLearningAgent(db, cfg)
    result_state = agent.run(state)

    return success_response({
        "response": result_state.tutor_response,
        "mode": result_state.response_mode,
        "metadata": result_state.response_metadata,
        "error": result_state.error,
    })


@tutor_bp.route("/explain", methods=["POST"])
def tutor_explain():
    data = request.get_json(silent=True) or {}
    data["response_mode"] = data.get("response_mode", "simple")
    if not data.get("message"):
        data["message"] = "Could you explain the main concepts covered in this lesson?"
    request.json_data = data
    return tutor_chat()


@tutor_bp.route("/quiz", methods=["POST"])
def tutor_quiz():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    if not session_id:
        return error_response("session_id is required.", 400, "MISSING_SESSION_ID")

    owner_id, _ = get_session_owner(request)
    db = Database.get_db()

    state = AgentState(
        session_id=str(session_id),
        owner_id=owner_id,
        student_message="Generate a multiple choice quiz question to test my understanding of this lesson.",
        request_type="quiz",
        response_mode="quiz",
        topic_id=data.get("topic_id"),
        lesson_id=data.get("lesson_id"),
    )

    cfg = current_app.config.get("EIT_CONFIG", config)
    agent = EITLearningAgent(db, cfg)
    result_state = agent.run(state)

    return success_response({
        "question": result_state.tutor_response,
        "mode": "quiz",
        "metadata": result_state.response_metadata,
    })


@tutor_bp.route("/feedback", methods=["POST"])
def tutor_feedback():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    question = sanitize_string(data.get("question", ""), max_length=1000)
    submitted_answer = sanitize_string(data.get("submitted_answer", ""), max_length=2000)

    if not session_id or not submitted_answer:
        return error_response("session_id and submitted_answer are required.", 400, "MISSING_FIELDS")

    owner_id, _ = get_session_owner(request)
    db = Database.get_db()

    prompt = (
        f"The question was: '{question}'\n"
        f"My answer is: '{submitted_answer}'\n"
        "Please evaluate my answer and give me helpful feedback."
    )

    state = AgentState(
        session_id=str(session_id),
        owner_id=owner_id,
        student_message=prompt,
        request_type="feedback",
        response_mode="feedback",
        topic_id=data.get("topic_id"),
        lesson_id=data.get("lesson_id"),
    )

    cfg = current_app.config.get("EIT_CONFIG", config)
    agent = EITLearningAgent(db, cfg)
    result_state = agent.run(state)

    # Record quiz attempt
    if db is not None:
        try:
            quiz_repo.create_quiz_attempt(db, {
                "session_id": str(session_id),
                "owner_id": owner_id,
                "topic_id": data.get("topic_id"),
                "lesson_id": data.get("lesson_id"),
                "question": question,
                "submitted_answer": submitted_answer,
                "feedback": result_state.tutor_response,
            })
        except Exception:
            pass

    return success_response({
        "feedback": result_state.tutor_response,
        "mode": "feedback",
        "metadata": result_state.response_metadata,
    })
