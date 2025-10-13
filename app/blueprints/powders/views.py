"""HTTP endpoints for the Powders blueprint."""

from flask import Response, jsonify, render_template, request

from app.repositories import powder_repo

from . import bp


@bp.route("/")
def index():
    """Powders inventory page."""
    query = request.args.get("q", "").strip() or None
    manufacturer = request.args.get("manufacturer", "").strip() or None
    powders = powder_repo.list_powders(query=query, manufacturer=manufacturer)
    return render_template(
        "powders/index.html",
        is_admin=True,
        powders=powders,
        total_powders=len(powders),
        filters={
            "query": query or "",
            "manufacturer": manufacturer or "",
        },
    )


@bp.get("/families.json")
def families_json():
    """Return distinct color families for powder colors.

    This provides the data expected by the legacy intake form to filter colors.
    """
    families = powder_repo.list_color_families()
    return jsonify(families or [])


@bp.get("/colors_full.json")
def colors_full_json():
    """Return an extended powder color listing suitable for client-side search.

    Each item should include `color` and may include `aliases` and `family`.
    """
    items = powder_repo.list_colors_full()
    return jsonify(items or [])


@bp.get("/by_color.json")
def by_color_json():
    """Return powders filtered by color query (legacy parity)."""
    q = request.args.get("q", "").strip()
    powders = powder_repo.list_powders(query=q or None)
    items = [
        {
            "id": p.id,
            "color": getattr(p, "powder_color", None),
            "manufacturer": getattr(p, "manufacturer", None),
            "product_code": getattr(p, "product_code", None),
        }
        for p in powders
    ]
    return jsonify(items)


@bp.get("/../powders.csv")
def legacy_powders_csv() -> Response:
    """Legacy CSV export for powders at /powders.csv.

    Delegates to a minimal CSV writer using repository data.
    """
    powders = powder_repo.list_powders()
    header = "id,manufacturer,color,on_hand_kg\n"
    rows = []
    for p in powders:
        manufacturer = (p.manufacturer or "").replace(",", " ")
        color_value = (getattr(p, "color", "") or "").replace(",", " ")
        on_hand = p.on_hand_kg or ""
        rows.append(f"{p.id},{manufacturer},{color_value},{on_hand}")
    csv_content = header + "\n".join(rows)
    return Response(
        csv_content,
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment; filename=powders.csv",
        },
    )
