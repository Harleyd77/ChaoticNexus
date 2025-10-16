"""HTTP endpoints for the Admin blueprint."""

from __future__ import annotations

import os
import secrets
from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy import select

from app.extensions import csrf
from app.models import User
from app.repositories import session_scope, settings_repo
from app.services.auth_service import _hash_password
from app.services.options_service import options_service
from app.services.settings_service import settings_service

from . import bp

ALLOWED_FAVICON_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "svg", "ico"}
ALLOWED_LOGO_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "svg"}


def _uploads_root() -> str:
    root = current_app.config.get("UPLOADS_DIR")
    if not root:
        raise RuntimeError("UPLOADS_DIR is not configured")
    return root


def _branding_dir() -> str:
    root = _uploads_root()
    directory = os.path.join(root, "branding")
    os.makedirs(directory, exist_ok=True)
    return directory


def _slugify(value: str) -> str:
    value = (value or "").strip().lower()
    return "-".join(filter(None, value.replace("_", "-").split())) or "brand"


def _generate_filename(original_name: str, suffix: str) -> str:
    base, ext = os.path.splitext(original_name or suffix)
    ext = ext.lower()
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    token = secrets.token_hex(4)
    safe_base = _slugify(base)[:40] or suffix
    return f"{safe_base}-{timestamp}-{token}{ext}"


def _save_branding_file(file_storage, *, allowed_exts: set[str], suffix: str) -> str:
    if not file_storage or not getattr(file_storage, "filename", None):
        raise ValueError("No file provided")

    filename = file_storage.filename or ""
    if "." not in filename:
        raise ValueError("Unsupported file type")
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed_exts:
        raise ValueError("Unsupported file type")

    final_name = _generate_filename(filename, suffix)
    directory = _branding_dir()
    abs_path = os.path.join(directory, final_name)
    file_storage.save(abs_path)

    relative = os.path.relpath(abs_path, _uploads_root()).replace("\\", "/")
    return relative


def _resolve_brand_asset(path: str | None) -> str | None:
    if not path:
        return None
    if path.startswith(("http://", "https://", "//")):
        return path
    return url_for("uploads", name=path)


@bp.route("/users")
def users():
    """User management page."""
    if not session.get("is_admin"):
        return redirect(url_for("auth.login", next=url_for("admin.users")))
    with session_scope() as db_session:
        rows = db_session.execute(select(User).order_by(User.username)).scalars().all()
    return render_template("admin/users.html", users=rows)


@bp.post("/users/<int:user_id>/save")
def users_save(user_id: int):
    """Save user admin flag and permissions."""
    if not session.get("is_admin"):
        return redirect(url_for("auth.login", next=url_for("admin.users")))
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

    with session_scope() as db_session:
        user = db_session.get(User, user_id)
        if not user:
            flash("User not found", "error")
            return redirect(url_for("admin.users"))
        user.is_admin = is_admin_flag
        user.permissions_json = {"perms": perms} if perms else None
        db_session.flush()

    flash("User updated", "success")
    return redirect(url_for("admin.users"))


@bp.post("/users/create")
def users_create():
    """Create a new admin/back-office user."""
    if not session.get("is_admin"):
        return redirect(url_for("auth.login", next=url_for("admin.users")))
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()
    is_admin_flag = request.form.get("is_admin") == "on"
    if not username or not password:
        flash("Username and password required", "error")
        return redirect(url_for("admin.users"))

    with session_scope() as db_session:
        exists = db_session.execute(
            select(User).filter(User.username == username)
        ).scalar_one_or_none()
        if exists:
            flash("Username already exists", "error")
            return redirect(url_for("admin.users"))
        user = User(
            username=username, password_hash=_hash_password(password), is_admin=is_admin_flag
        )
        db_session.add(user)
        db_session.flush()

    flash("User created", "success")
    return redirect(url_for("admin.users"))


@bp.route("/settings", methods=["GET", "POST"])
def settings():
    """Application settings page."""
    if not session.get("is_admin") and request.method != "POST":
        return redirect(url_for("auth.login", next=url_for("admin.settings")))

    if request.method == "POST":
        if not session.get("is_admin"):
            return redirect(url_for("auth.login", next=url_for("admin.settings")))
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
    return render_template(
        "admin/settings.html",
        settings=payload,
        job_options=job_options,
        branding_favicon=_resolve_brand_asset(payload.favicon_path),
        branding_page_logo=_resolve_brand_asset(payload.page_logo_path),
    )


@bp.post("/branding/favicon")
@csrf.exempt
def branding_favicon_upload():
    if not session.get("is_admin"):
        return redirect(url_for("auth.login", next=url_for("admin.settings")))

    file_storage = request.files.get("file")
    try:
        relative_path = _save_branding_file(
            file_storage, allowed_exts=ALLOWED_FAVICON_EXTENSIONS, suffix="favicon"
        )
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("admin.settings"))
    except Exception:
        flash("Failed to upload favicon.", "error")
        return redirect(url_for("admin.settings"))

    settings_repo.set_setting("branding:favicon", relative_path)
    flash("Favicon updated.", "success")
    return redirect(url_for("admin.settings"))


@bp.post("/branding/favicon/clear")
@csrf.exempt
def branding_favicon_clear():
    if not session.get("is_admin"):
        return redirect(url_for("auth.login", next=url_for("admin.settings")))

    settings_repo.set_setting("branding:favicon", "")
    flash("Favicon cleared.", "success")
    return redirect(url_for("admin.settings"))


@bp.post("/branding/page-logo")
@csrf.exempt
def branding_page_logo_upload():
    if not session.get("is_admin"):
        return redirect(url_for("auth.login", next=url_for("admin.settings")))

    file_storage = request.files.get("file")
    try:
        relative_path = _save_branding_file(
            file_storage, allowed_exts=ALLOWED_LOGO_EXTENSIONS, suffix="logo"
        )
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("admin.settings"))
    except Exception:
        flash("Failed to upload logo.", "error")
        return redirect(url_for("admin.settings"))

    settings_repo.set_setting("branding:page_logo", relative_path)
    flash("Page logo updated.", "success")
    return redirect(url_for("admin.settings"))


@bp.post("/branding/page-logo/clear")
@csrf.exempt
def branding_page_logo_clear():
    if not session.get("is_admin"):
        return redirect(url_for("auth.login", next=url_for("admin.settings")))

    settings_repo.set_setting("branding:page_logo", "")
    flash("Page logo cleared.", "success")
    return redirect(url_for("admin.settings"))


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
