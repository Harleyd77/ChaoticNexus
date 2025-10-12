"""HTTP endpoints for the Inventory blueprint."""

from flask import render_template

from . import bp


@bp.route("/")
def index():
    """Inventory management page."""
    # TODO: Load from repository once implemented
    return render_template(
        "inventory/index.html",
        is_admin=True,
        powders=[],
        total_powders=0,
        in_stock=[],
        low_stock=[],
        out_of_stock=[],
        low_stock_threshold=5.0,
    )
