"""Application factory for the Chaotic Nexus backend."""

from __future__ import annotations

import logging
from typing import Any

from flask import Flask

from .config import get_config
from .extensions import csrf, db, migrate


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__, static_folder="static", template_folder="templates")

    config_class = get_config(config_name)
    app.config.from_object(config_class)

    _configure_logging(app)
    _register_extensions(app)
    _register_blueprints(app)
    _register_cli(app)
    _register_routes(app)

    return app


def _configure_logging(app: Flask) -> None:
    """Set up application logging according to LOG_LEVEL."""
    level_name = app.config.get("LOG_LEVEL", "INFO")
    level = getattr(logging, str(level_name).upper(), logging.INFO)
    app.logger.setLevel(level)
    for handler in app.logger.handlers:
        handler.setLevel(level)


def _register_extensions(app: Flask) -> None:
    """Initialise Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Ensure SQLAlchemy models are imported so metadata is registered with the app.
    with app.app_context():
        from . import models  # noqa: F401  # pylint: disable=unused-import


def _register_blueprints(app: Flask) -> None:
    """Register HTTP blueprints."""
    from .blueprints.admin import bp as admin_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.customer_portal import bp as customer_portal_bp
    from .blueprints.customers import bp as customers_bp
    from .blueprints.dashboard import bp as dashboard_bp
    from .blueprints.intake import bp as intake_bp
    from .blueprints.inventory import bp as inventory_bp
    from .blueprints.jobs import bp as jobs_bp
    from .blueprints.powders import bp as powders_bp
    from .blueprints.sprayer import bp as sprayer_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_portal_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(intake_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(powders_bp)
    app.register_blueprint(sprayer_bp)


def _register_cli(app: Flask) -> None:
    """Attach custom CLI commands."""
    from . import cli

    app.cli.add_command(cli.hello)
    app.cli.add_command(cli.seed_data)


def _register_routes(app: Flask) -> None:
    """Register lightweight routes that do not warrant blueprints."""
    from flask import redirect, url_for

    @app.get("/")
    def index():
        """Redirect root to dashboard."""
        return redirect(url_for("dashboard.index"))

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        """Container health check endpoint."""
        return {"ok": True}
