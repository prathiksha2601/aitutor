"""
app/routes/health.py
Health-check endpoint. Always returns 200; reports component statuses.
"""

from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify

from app.database import Database

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health():
    """
    GET /api/health

    Returns system health information. Always 200 so load balancers
    can distinguish between 'app is up but degraded' and 'app is down'.
    """
    cfg = current_app.config.get("EIT_CONFIG")

    db_connected = Database.health_check()

    openai_configured = bool(cfg and cfg.OPENAI_API_KEY)
    model_configured = bool(cfg and cfg.MODEL_PATH)

    payload = {
        "success": True,
        "data": {
            "status": "ok" if db_connected else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "db_connected": db_connected,
            "services": {
                "openai_configured": openai_configured,
                "model_configured": model_configured,
            },
        },
    }
    return jsonify(payload), 200
