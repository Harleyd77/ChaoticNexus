"""HTTP endpoints for the Powders blueprint."""

from flask import Response, flash, jsonify, redirect, render_template, request, url_for

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


@bp.get("/<int:powder_id>.json")
def powder_detail_json(powder_id: int):
    """Return powder detail JSON for a single powder (legacy parity shape)."""
    p = powder_repo.get_powder(powder_id)
    if not p:
        return jsonify({}), 404
    return jsonify(
        {
            "id": p.id,
            "powder_color": getattr(p, "powder_color", None),
            "manufacturer": getattr(p, "manufacturer", None),
            "product_code": getattr(p, "product_code", None),
            "gloss_level": getattr(p, "gloss_level", None),
            "finish": getattr(p, "finish", None),
            "metallic": getattr(p, "metallic", None),
            "needs_clear": getattr(p, "needs_clear", None),
            "int_ext": getattr(p, "int_ext", None),
            "additional_code": getattr(p, "additional_code", None),
            "on_hand_kg": float(p.on_hand_kg or 0),
            "last_weighed_kg": float(p.last_weighed_kg or 0),
            "last_weighed_at": getattr(p, "last_weighed_at", None),
            "in_stock": float(p.in_stock or 0),
            "weight_box_kg": float(p.weight_box_kg or 0),
            "picture_url": getattr(p, "picture_url", None),
            "msds_url": getattr(p, "msds_url", None),
            "sds_url": getattr(p, "sds_url", None),
            "web_link": getattr(p, "web_link", None),
            "notes": getattr(p, "notes", None),
            "additional_info": getattr(p, "additional_info", None),
            "cure_schedule": getattr(p, "cure_schedule", None),
        }
    )


@bp.post("/import")
def import_csv():
    """Stub CSV import endpoint for parity: accepts file and flashes message."""
    file = request.files.get("file")
    if not file:
        flash("No file uploaded", "error")
        return redirect(url_for("powders.index"))
    # Parity stub: do not parse; acknowledge upload
    flash("CSV import received (parity stub)", "success")
    return redirect(url_for("powders.index"))


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
    """Return powder by exact color name with in_stock value (legacy expects this)."""
    name = (request.args.get("name") or request.args.get("q") or "").strip()
    if not name:
        return jsonify({}), 200
    hit = powder_repo.find_by_color_name(name)
    if not hit:
        return jsonify({}), 200
    return jsonify(
        {
            "id": hit.id,
            "color": getattr(hit, "powder_color", None),
            "manufacturer": getattr(hit, "manufacturer", None),
            "product_code": getattr(hit, "product_code", None),
            "in_stock": float(hit.on_hand_kg or hit.in_stock or 0),
        }
    )


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
