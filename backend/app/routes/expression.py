"""
app/routes/expression.py
Facial-expression analysis and session signals routes.
STRICT consent-gated. Never stores raw webcam frames by default.
Treats predictions as uncertain, secondary signals.
"""

from flask import Blueprint, request
from app.database import Database
from app.config import config
from app.computer_vision.inference import ExpressionInference
from app.computer_vision.gaze import GazeEstimator
from app.repositories import expression_repo, sessions_repo
from app.security.auth import get_session_owner
from app.utils.responses import success_response, error_response

expression_bp = Blueprint("expression", __name__, url_prefix="/api/expression")

# Initialise inference services
_inference_service = ExpressionInference(config.MODEL_PATH, config.MODEL_LABELS_PATH)
_gaze_service = GazeEstimator()


@expression_bp.route("/analyze", methods=["POST"])
def analyze_expression():
    """
    Perform server-side expression inference on a single frame.
    STRICTLY requires informed consent. Does NOT store the image.
    """
    data = request.get_json(silent=True) or {}
    consent = data.get("consent", False)

    if not consent:
        return error_response(
            "Webcam analysis requires explicit user consent.",
            403,
            "CONSENT_REQUIRED",
        )

    image_b64 = data.get("image_b64")
    if not image_b64:
        return error_response("image_b64 is required.", 400, "MISSING_IMAGE")

    # Limit image payload size (< 1MB base64)
    if len(image_b64) > 1_000_000:
        return error_response("Image payload too large (max 500KB decoded).", 413, "PAYLOAD_TOO_LARGE")

    try:
        image_bytes = ExpressionInference.decode_base64(image_b64)
    except Exception:
        return error_response("Invalid base64 image data.", 400, "INVALID_IMAGE")

    # Run MobileNetV2 inference
    prediction = _inference_service.predict(image_bytes)

    # Run optional gaze estimation
    gaze_result = _gaze_service.estimate_gaze(image_bytes)

    return success_response({
        "expression": prediction,
        "gaze": gaze_result,
        "uncertain_signal_notice": (
            "Facial expression and gaze predictions are uncertain, optional signals. "
            "They do not establish emotion, comprehension, or mental state."
        ),
    })


@expression_bp.route("/session", methods=["POST"])
def store_session_summary():
    """
    Persist aggregated expression summary only when explicit consent is present.
    """
    data = request.get_json(silent=True) or {}
    consent = data.get("consent", False)

    if not consent:
        return error_response("Consent required to store expression summary.", 403, "CONSENT_REQUIRED")

    session_id = data.get("session_id")
    if not session_id:
        return error_response("session_id is required.", 400, "MISSING_SESSION_ID")

    owner_id, _ = get_session_owner(request)
    db = Database.get_db()
    if db is None:
        return error_response("Database unavailable.", 503, "DB_UNAVAILABLE")

    if not sessions_repo.verify_session_ownership(db, session_id, owner_id):
        return error_response("Forbidden: You do not own this session.", 403, "FORBIDDEN")

    summary_data = {
        "session_id": session_id,
        "owner_id": owner_id,
        "consent": True,
        "aggregated_category_counts": data.get("aggregated_category_counts", {}),
        "quality_metadata": data.get("quality_metadata", {}),
        "model_version": "1.0.0",
    }

    stored = expression_repo.create_expression_summary(db, summary_data)
    return success_response({"summary": stored}, 201, "Summary stored.")
