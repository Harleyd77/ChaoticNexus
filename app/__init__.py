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
    from .blueprints.print_templates import bp as print_templates_bp
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
    app.register_blueprint(print_templates_bp)


def _register_cli(app: Flask) -> None:
    """Attach custom CLI commands."""
    from . import cli

    app.cli.add_command(cli.hello)
    app.cli.add_command(cli.seed_data)
    app.cli.add_command(cli.create_admin)


def _register_routes(app: Flask) -> None:
    """Register lightweight routes that do not warrant blueprints."""
    import json
    import os

    from flask import jsonify, redirect, request, send_file, send_from_directory, url_for

    @app.get("/")
    def index():
        """Redirect root to dashboard."""
        return redirect(url_for("dashboard.index"))

    @app.get("/nav")
    def legacy_nav() -> Any:
        """Legacy navigation endpoint redirecting to dashboard.

        Maintains compatibility with ChaoticNexus-Orig while preferring a
        same-method permanent redirect.
        """
        return redirect(url_for("dashboard.index"), code=308)

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        """Container health check endpoint."""
        return {"ok": True}

    @app.get("/favicon.ico")
    def favicon() -> Any:
        """Serve favicon for legacy agents and browsers requesting /favicon.ico."""
        static_dir = os.path.join(app.root_path, "static", "img")
        # Prefer .ico if available to match legacy clients; fall back to .png.
        ico_path = os.path.join(static_dir, "favicon.ico")
        if os.path.exists(ico_path):  # pragma: no cover - environment dependent
            return send_from_directory(static_dir, "favicon.ico")
        return send_from_directory(static_dir, "favicon.png")

    @app.get("/uploads/<path:name>")
    def uploads(name: str):
        """Serve uploaded files from configured UPLOADS_DIR for legacy parity."""
        upload_root = app.config.get("UPLOADS_DIR")
        path = os.path.join(upload_root, name)
        if not os.path.abspath(path).startswith(os.path.abspath(upload_root)):
            # Prevent path traversal
            return {"error": "invalid path"}, 400
        if not os.path.exists(path):
            return {"error": "not found"}, 404
        return send_file(path)

    # Legacy CSV endpoints at top-level paths
    @app.get("/jobs.csv")
    def legacy_jobs_csv_top():
        from .blueprints.jobs.views import export_csv as jobs_export

        return jobs_export()

    @app.get("/powders.csv")
    def legacy_powders_csv_top():
        from .blueprints.powders.views import legacy_powders_csv

        return legacy_powders_csv()

    # Legacy intake paths → new intake blueprint
    @app.get("/intake_form")
    def legacy_intake_form():
        return redirect(url_for("intake.intake_form"), code=308)

    @app.get("/railing_intake")
    def legacy_railing_intake():
        return redirect(url_for("intake.railing_intake"), code=308)

    # Legacy config JSON endpoints (no /admin prefix per legacy app)
    @app.get("/config/intake.json")
    def get_intake_config():
        from app.repositories.settings import settings_repo

        row = settings_repo.get_setting("config:intake")
        try:
            data = json.loads(row.value) if row and row.value else {}
        except Exception:  # pragma: no cover - defensive
            data = {}
        return jsonify(data)

    @app.post("/config/intake")
    def set_intake_config():
        from app.repositories.settings import settings_repo

        payload = request.get_json(silent=True) or {}
        settings_repo.set_setting("config:intake", json.dumps(payload))
        return jsonify({"ok": True})

    @app.get("/config/railing.json")
    def get_railing_config():
        from app.repositories.settings import settings_repo

        row = settings_repo.get_setting("config:railing")
        try:
            data = json.loads(row.value) if row and row.value else {}
        except Exception:  # pragma: no cover - defensive
            data = {}
        return jsonify(data)

    @app.post("/config/railing")
    def set_railing_config():
        from app.repositories.settings import settings_repo

        payload = request.get_json(silent=True) or {}
        settings_repo.set_setting("config:railing", json.dumps(payload))
        return jsonify({"ok": True})
