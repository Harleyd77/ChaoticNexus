"""HTTP endpoints for the Admin blueprint."""

from flask import render_template

from . import bp


@bp.route("/users")
def users():
    """User management page."""
    # TODO: Load from repository once implemented
    return render_template(
        "admin/users.html",
        users=[],
    )


@bp.route("/settings")
def settings():
    """Application settings page."""
    # TODO: Load from repository once implemented
    return render_template(
        "admin/settings.html",
        settings={},
    )
