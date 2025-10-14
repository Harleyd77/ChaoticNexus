"""HTTP endpoints for the Admin blueprint."""

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select

from app.models import User
from app.repositories import session_scope
from app.services.auth_service import _hash_password
from app.services.options_service import options_service
from app.services.settings_service import settings_service

from . import bp


@bp.route("/users")
def users():
    """User management page."""
    with session_scope() as session:
        rows = session.execute(select(User).order_by(User.username)).scalars().all()
    return render_template("admin/users.html", users=rows)


@bp.post("/users/<int:user_id>/save")
def users_save(user_id: int):
    """Save user admin flag and permissions."""
    perms = []
    for key in [
        "see_jobs",
        "see_powders",
        "see_inventory",
        "edit_options",
        "manage_users",
    ]:
        if request.form.get(key) == "on":
            perms.append(key)

    is_admin_flag = request.form.get("is_admin") == "on"

    with session_scope() as session:
        user = session.get(User, user_id)
        if not user:
            flash("User not found", "error")
            return redirect(url_for("admin.users"))
        user.is_admin = is_admin_flag
        user.permissions_json = {"perms": perms} if perms else None
        session.flush()

    flash("User updated", "success")
    return redirect(url_for("admin.users"))


@bp.post("/users/create")
def users_create():
    """Create a new admin/back-office user."""
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()
    is_admin_flag = request.form.get("is_admin") == "on"
    if not username or not password:
        flash("Username and password required", "error")
        return redirect(url_for("admin.users"))

    with session_scope() as session:
        exists = session.execute(
            select(User).filter(User.username == username)
        ).scalar_one_or_none()
        if exists:
            flash("Username already exists", "error")
            return redirect(url_for("admin.users"))
        user = User(
            username=username, password_hash=_hash_password(password), is_admin=is_admin_flag
        )
        session.add(user)
        session.flush()

    flash("User created", "success")
    return redirect(url_for("admin.users"))


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
