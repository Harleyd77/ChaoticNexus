from __future__ import annotations

import json

from flask import current_app, redirect, request, session, url_for

from .db import db_query_one

PERM_DEFAULTS = {
    "see_intake": False,
    "see_railing": False,
    "see_jobs": False,
    "see_job_screen": False,
    "see_archived": False,
    "see_powders": False,
    "see_customers": False,
    "see_csv": False,
}

_PUBLIC_ATTR = "_powder_public_endpoint"


def public_endpoint(view_func):
    setattr(view_func, _PUBLIC_ATTR, True)
    return view_func


def _is_public_endpoint(endpoint: str) -> bool:
    if not endpoint:
        return False
    view_func = current_app.view_functions.get(endpoint)
    if not view_func:
        return False
    return bool(getattr(view_func, _PUBLIC_ATTR, False))


def is_admin() -> bool:
    return bool(session.get("is_admin"))


def get_current_username() -> str | None:
    """Get the username of the currently logged-in user."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        row = db_query_one("SELECT username FROM users WHERE id=?", (user_id,))
        return row["username"] if row else None
    except Exception:
        return None


def require_admin():
    if not is_admin():
        return redirect(url_for("auth.login", next=request.path))
    return None


def _load_user_perms(user_id: int, is_admin_flag: bool) -> dict:
    if is_admin_flag:
        return {key: True for key in PERM_DEFAULTS}
    try:
        row = db_query_one("SELECT permissions_json FROM users WHERE id=?", (user_id,))
    except Exception as exc:
        print(f"[PowderApp][WARN] Failed to load permissions for user {user_id}: {exc}")
        return dict(PERM_DEFAULTS)
    if not row:
        return dict(PERM_DEFAULTS)
    try:
        data = json.loads(row["permissions_json"] or "{}")
        loaded = {key: bool(value) for key, value in (data or {}).items()}
    except Exception:
        loaded = {}
    merged = dict(PERM_DEFAULTS)
    merged.update(loaded)
    return merged


def current_perms() -> dict:
    user_id = session.get("user_id")
    if not (user_id or session.get("is_admin")):
        return {key: False for key in PERM_DEFAULTS}
    return _load_user_perms(int(user_id) if user_id else 0, bool(session.get("is_admin")))


def has_perm(key: str) -> bool:
    if is_admin():
        return True
    return bool(current_perms().get(key, False))


def is_logged_in() -> bool:
    if session.get("is_admin") or session.get("user_id"):
        return True
    if session.get("customer_id") and session.get("customer_session_token"):
        return True
    return False


def _require_login_globally():
    endpoint = request.endpoint or ""

    if endpoint.startswith("static"):
        return None

    if _is_public_endpoint(endpoint):
        return None

    if not is_logged_in():
        next_url = request.full_path if request.full_path else request.path
        # Always redirect to React login
        return redirect("/react/login?next=" + next_url)
    return None


def register_security(app) -> None:
    app.before_request(_require_login_globally)
