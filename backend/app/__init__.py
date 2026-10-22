"""
app/__init__.py
Flask application factory for the EIT backend.
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import Config
from app.database import Database
from app.database.indexes import create_all_indexes

logger = logging.getLogger(__name__)


def create_app(config: Config | None = None) -> Flask:
    """
    Application factory.

    Args:
        config: Optional Config instance (useful for testing).

    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    cfg = config or Config()
    app.config["SECRET_KEY"] = cfg.SECRET_KEY
    app.config["DEBUG"] = cfg.DEBUG
    # Store full config object for access in routes / services
    app.config["EIT_CONFIG"] = cfg

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    logging.basicConfig(
        level=logging.DEBUG if cfg.DEBUG else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # ------------------------------------------------------------------
    # MongoDB
    # ------------------------------------------------------------------
    try:
        Database.connect(cfg.MONGODB_URI, cfg.MONGODB_DATABASE)
        db = Database.get_db()
        create_all_indexes(db)
    except Exception as exc:  # noqa: BLE001
        logger.error("Database initialisation error: %s", exc)
        # App still starts; health endpoint reports db_connected=False

    # ------------------------------------------------------------------
    # CORS – strict origin
    # ------------------------------------------------------------------
    CORS(
        app,
        origins=[cfg.FRONTEND_ORIGIN],
        supports_credentials=True,
        methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Session-ID", "X-Request-ID"],
    )

    # ------------------------------------------------------------------
    # Rate limiter
    # ------------------------------------------------------------------
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=[f"{cfg.RATE_LIMIT_PER_MINUTE} per minute"],
        storage_uri="memory://",
    )
    app.config["LIMITER"] = limiter  # expose for blueprint use

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.topics import topics_bp
    from app.routes.sessions import sessions_bp
    from app.routes.progress import progress_bp
    from app.routes.tutor import tutor_bp
    from app.routes.expression import expression_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(topics_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(tutor_bp)
    app.register_blueprint(expression_bp)

    # ------------------------------------------------------------------
    # JSON error handlers – never expose stack traces
    # ------------------------------------------------------------------
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": {"message": "Bad request", "code": "BAD_REQUEST"}}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"success": False, "error": {"message": "Unauthorized", "code": "UNAUTHORIZED"}}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "error": {"message": "Forbidden", "code": "FORBIDDEN"}}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": {"message": "Resource not found", "code": "NOT_FOUND"}}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": {"message": "Method not allowed", "code": "METHOD_NOT_ALLOWED"}}), 405

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({"success": False, "error": {"message": "Too many requests", "code": "RATE_LIMITED"}}), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.error("Internal server error: %s", e)
        return jsonify({"success": False, "error": {"message": "Internal server error", "code": "INTERNAL_ERROR"}}), 500

    logger.info("EIT Flask application created (env=%s)", cfg.FLASK_ENV)
    return app
