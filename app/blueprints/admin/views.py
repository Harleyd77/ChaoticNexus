"""HTTP endpoints for the Admin blueprint."""

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select

from app.models import User
from app.repositories import session_scope
from app.services.options_service import options_service
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
    job_options = options_service.get_job_form_options()
    return render_template("admin/settings.html", settings=payload, job_options=job_options)


@bp.get("/options/drawer")
def options_drawer():
    name = (request.args.get("name") or "").strip()
    items = options_service.get_job_option_list(name)
    return render_template("admin/_options_drawer.html", name=name, items=items)


@bp.post("/options/save")
def options_save():
    name = (request.form.get("name") or "").strip()
    items_raw = request.form.get("items") or ""
    items = [line.strip() for line in items_raw.splitlines()]
    options_service.set_job_option_list(name, items)
    return render_template(
        "admin/_options_drawer_saved.html",
        name=name,
        items=options_service.get_job_option_list(name),
    )
