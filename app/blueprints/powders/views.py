"""HTTP endpoints for the Powders blueprint."""

from flask import render_template, request

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
