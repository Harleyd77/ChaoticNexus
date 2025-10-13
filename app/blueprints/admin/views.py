"""HTTP endpoints for the Admin blueprint."""

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select

from app.models import User
from app.repositories import session_scope
from app.services.settings_service import settings_service

from . import bp


@bp.route("/users")
def users():
    """User management page."""
    with session_scope() as session:
        rows = session.execute(select(User).order_by(User.username)).scalars().all()
    return render_template("admin/users.html", users=rows)


@bp.route("/settings", methods=["GET", "POST"])
def settings():
    """Application settings page."""
    if request.method == "POST":
        try:
            settings_service.update_settings(
                company_name=request.form.get("company_name"),
                brand_primary=request.form.get("brand_primary"),
                brand_accent=request.form.get("brand_accent"),
                logo_url=request.form.get("logo_url"),
            )
        except ValueError as error:
            flash(str(error), "error")
        else:
            flash("Settings updated successfully", "success")
            return redirect(url_for("admin.settings"))

    payload = settings_service.get_settings()

    return render_template(
        "admin/settings.html",
        settings=payload,
    )
