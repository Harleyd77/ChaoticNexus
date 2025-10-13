"""HTTP endpoints for the Admin blueprint."""

from flask import flash, redirect, render_template, request, url_for

from app.services.settings_service import settings_service

from . import bp


@bp.route("/users")
def users():
    """User management page."""
    # TODO: Load from repository once implemented
    return render_template(
        "admin/users.html",
        users=[],
    )


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
