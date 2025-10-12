"""HTTP endpoints for the Customers blueprint."""

from flask import render_template

from . import bp


@bp.route("/")
def index():
    """Customers list page."""
    # TODO: Load from repository once implemented
    return render_template(
        "customers/index.html",
        is_admin=True,
        customers=[],
    )
