"""HTTP endpoints for the Inventory blueprint."""

from flask import jsonify, render_template, request

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


@bp.get("/api/powders")
def api_powders():
    """Return powder inventory data for UI tables (parity JSON)."""
    search = request.args.get("search") or None
    manufacturer = request.args.get("manufacturer") or None
    threshold_param = request.args.get("threshold")
    try:
        low_stock_threshold = float(threshold_param) if threshold_param else 5.0
    except ValueError:  # pragma: no cover - defensive
        low_stock_threshold = 5.0

    powders, summary = inventory_service.powders_dashboard(
        search=search,
        manufacturer=manufacturer,
        low_stock_threshold=low_stock_threshold,
    )
    data = [
        {
            "id": p.id,
            "color": getattr(p, "powder_color", None),
            "manufacturer": getattr(p, "manufacturer", None),
            "on_hand_kg": float(p.on_hand_kg or 0),
            "in_stock": float(p.in_stock or 0),
            "family": getattr(p, "color_family", None),
        }
        for p in powders
    ]
    return jsonify(
        {
            "summary": {
                "total": summary.total_powders,
                "in_stock": summary.in_stock,
                "low_stock": summary.low_stock,
                "out_of_stock": summary.out_of_stock,
                "low_stock_threshold": summary.low_stock_threshold,
            },
            "powders": data,
        }
    )


@bp.get("/api/reorder")
def api_reorder():
    """Return powders requiring reorder based on threshold."""
    threshold_param = request.args.get("threshold")
    try:
        low_stock_threshold = float(threshold_param) if threshold_param else 5.0
    except ValueError:  # pragma: no cover
        low_stock_threshold = 5.0
    powders, _ = inventory_service.powders_dashboard(low_stock_threshold=low_stock_threshold)
    need_reorder = [
        {
            "id": p.id,
            "color": getattr(p, "powder_color", None),
            "manufacturer": getattr(p, "manufacturer", None),
            "on_hand_kg": float(p.on_hand_kg or 0),
        }
        for p in powders
        if (p.on_hand_kg or 0) <= low_stock_threshold
    ]
    return jsonify({"items": need_reorder})


@bp.get("/history/<int:powder_id>")
def history(powder_id: int):
    """Inventory history for a given powder (HTML view)."""
    logs = inventory_service.recent_logs(powder_id, limit=200)
    return render_template(
        "inventory/history.html",
        is_admin=True,
        logs=logs,
        powder_id=powder_id,
    )


@bp.get("/reorder")
def reorder_view():
    """HTML view listing powders to reorder."""
    threshold_param = request.args.get("threshold")
    try:
        low_stock_threshold = float(threshold_param) if threshold_param else 5.0
    except ValueError:  # pragma: no cover
        low_stock_threshold = 5.0
    powders, _ = inventory_service.powders_dashboard(low_stock_threshold=low_stock_threshold)
    need_reorder = [p for p in powders if (p.on_hand_kg or 0) <= low_stock_threshold]
    return render_template(
        "inventory/reorder.html",
        is_admin=True,
        items=need_reorder,
        low_stock_threshold=low_stock_threshold,
    )


@bp.post("/<int:powder_id>/update")
def update_powder(powder_id: int):
    """Update stock to an absolute value from form post."""
    try:
        new_value = float(request.form.get("on_hand_kg", "0") or "0")
    except ValueError:
        new_value = 0.0
    inventory_service.record_stock_update(
        powder_id, new_value=new_value, actor="web", notes=request.form.get("notes")
    )
    return render_template(
        "inventory/index.html",
        is_admin=True,
        powders=inventory_service.powders_dashboard()[0],
        total_powders=inventory_service.powders_dashboard()[1].total_powders,
        in_stock=[],
        low_stock=[],
        out_of_stock=[],
        low_stock_threshold=5.0,
    )


@bp.post("/<int:powder_id>/adjust")
def adjust_powder(powder_id: int):
    """Adjust stock by delta from form post."""
    try:
        delta = float(request.form.get("delta", "0") or "0")
    except ValueError:
        delta = 0.0
    powders, _ = inventory_service.powders_dashboard()
    current = next((p for p in powders if p.id == powder_id), None)
    current_value = float(getattr(current, "on_hand_kg", 0) or 0)
    new_value = current_value + delta
    inventory_service.record_stock_update(
        powder_id, new_value=new_value, actor="web", notes=request.form.get("notes")
    )
    return jsonify({"ok": True, "powder_id": powder_id, "new_value": new_value})


@bp.post("/api/update")
def api_update():
    """Update powder stock level; returns updated record and log id."""
    json_data = request.get_json(silent=True) or {}
    powder_id = int(json_data.get("powder_id"))
    new_value = float(json_data.get("on_hand_kg"))
    actor = json_data.get("actor")
    notes = json_data.get("notes")
    log = inventory_service.record_stock_update(
        powder_id, new_value=new_value, actor=actor, notes=notes
    )
    return jsonify({"log_id": log.id}), 200
