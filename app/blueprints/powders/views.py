"""HTTP endpoints for the Powders blueprint."""

from flask import render_template

from . import bp


@bp.route("/")
def index():
    """Powders inventory page."""
    # TODO: Load from repository once implemented
    return render_template(
        "powders/index.html",
        is_admin=True,
        powders=[],
        total_powders=0,
    )
