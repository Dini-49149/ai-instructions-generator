"""Flask application entrypoint for the AI Instructions Generator web service."""
from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from ai_instructions_app.api.routes.health import health_bp
from ai_instructions_app.api.routes.workflow import workflow_bp
from ai_instructions_app.config.logging import configure_logging
from ai_instructions_app.config.settings import get_settings
from ai_instructions_app.models.database import db


def create_app() -> Flask:
    """Create and configure the Flask application instance."""
    settings = get_settings()
    configure_logging(settings)

    app = Flask(__name__)
    app.config.from_object(settings)

    db.init_app(app)
    CORS(app)

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(workflow_bp, url_prefix="/api/v1/workflow")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
