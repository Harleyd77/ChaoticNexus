"""HTTP endpoints for the Inventory blueprint."""

from flask import render_template, request

from app.services.inventory_service import inventory_service

from . import bp


@bp.route("/")
def index():
    """Inventory management page."""
    search = request.args.get("search")
    manufacturer = request.args.get("manufacturer")
    threshold_param = request.args.get("threshold")

    try:
        low_stock_threshold = float(threshold_param) if threshold_param else 5.0
    except ValueError:  # pragma: no cover - defensive
        low_stock_threshold = 5.0

    powders, summary = inventory_service.powders_dashboard(
        search=search or None,
        manufacturer=manufacturer or None,
        low_stock_threshold=low_stock_threshold,
    )

    in_stock = []
    low_stock = []
    out_of_stock = []

    for powder in powders:
        stock_value = powder.on_hand_kg or powder.in_stock or 0
        if stock_value <= 0:
            out_of_stock.append(powder)
        elif stock_value <= low_stock_threshold:
            low_stock.append(powder)
        else:
            in_stock.append(powder)

    return render_template(
        "inventory/index.html",
        is_admin=True,
        powders=powders,
        total_powders=summary.total_powders,
        in_stock=in_stock,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        low_stock_threshold=summary.low_stock_threshold,
    )
