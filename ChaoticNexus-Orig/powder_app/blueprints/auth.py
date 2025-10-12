from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from ..core.branding import get_branding_settings
from ..core.customer_auth import (
    authenticate_customer_credentials,
    end_customer_session,
    get_current_customer,
    is_customer_logged_in,
    start_customer_session,
)
from ..core.db import INTEGRITY_ERRORS, db_execute, db_query_one
from ..core.security import public_endpoint

bp = Blueprint("auth", __name__)

_ADMIN_SESSION_KEYS = ("user_id", "username", "is_admin")


def _users_enabled() -> bool:
    try:
        row = db_query_one("SELECT COUNT(*) AS c FROM users")
        return (row["c"] or 0) > 0
    except Exception:
        return False


def _clear_session_keys(keys: tuple[str, ...]) -> None:
    for key in keys:
        session.pop(key, None)


def _set_admin_session(user: dict) -> None:
    _clear_session_keys(_ADMIN_SESSION_KEYS)
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["is_admin"] = bool(user["is_admin"])


def _login_branding() -> tuple[str, str]:
    branding = get_branding_settings()
    login_bg = (branding.get("login_bg") or "").strip()
    login_title = branding.get("login_title") or "Victoria Powder Coating Ltd"
    login_bg_url = url_for("base.uploaded_file", name=login_bg) if login_bg else ""
    return login_title, login_bg_url


@bp.route("/login", methods=["GET", "POST"], endpoint="login")
@public_endpoint
def login_view():
    # Redirect GET requests to React login
    if request.method == "GET":
        next_url = request.args.get("next", "")
        if next_url:
            return redirect(f"/react/login?next={next_url}")
        return redirect("/react/login")

    # Handle POST for backwards compatibility (if needed)
    users_exist = _users_enabled()
    login_title, login_bg_url = _login_branding()
    customer_logged_in = is_customer_logged_in()
    customer_info = get_current_customer() if customer_logged_in else None

    if request.method == "POST":
        if not users_exist and request.form.get("setup_admin") == "1":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            if not username or not password:
                flash("Username and password are required", "error")
            else:
                try:
                    db_execute(
                        "INSERT INTO users (username, password_hash, is_admin, created_at) VALUES (?,?,1,?)",
                        (username, generate_password_hash(password), datetime.now().isoformat()),
                    )
                except INTEGRITY_ERRORS:
                    flash("Username already exists", "error")
                else:
                    user = db_query_one(
                        "SELECT * FROM users WHERE lower(trim(username)) = lower(trim(?))",
                        (username,),
                    )
                    if user:
                        end_customer_session()
                        _set_admin_session(user)
                        destination = request.args.get("next") or url_for("base.nav")
                        return redirect(destination)
        else:
            identifier = (
                request.form.get("identifier")
                or request.form.get("username")
                or request.form.get("email")
                or ""
            ).strip()
            password = request.form.get("password") or ""

            if not identifier or not password:
                flash("Email or username and password are required", "error")
            else:
                user = db_query_one(
                    "SELECT * FROM users WHERE lower(trim(username)) = lower(trim(?))",
                    (identifier,),
                )

                if user and check_password_hash(user["password_hash"], password):
                    end_customer_session()
                    _set_admin_session(user)
                    destination = request.args.get("next") or url_for("base.nav")
                    return redirect(destination)

                customer_record, customer_error = authenticate_customer_credentials(
                    identifier.lower(), password
                )
                if customer_record:
                    _clear_session_keys(_ADMIN_SESSION_KEYS)
                    start_customer_session(customer_record)
                    flash(f"Welcome back, {customer_record['first_name']}!", "success")
                    destination = request.args.get("next") or url_for("customer_portal.dashboard")
                    return redirect(destination)

                if customer_error and not customer_error.lower().startswith("invalid"):
                    flash(customer_error, "error")
                else:
                    flash("Invalid login credentials", "error")

    return render_template(
        "auth/login.html",
        first_run=(not users_exist),
        login_bg_url=login_bg_url,
        login_title=login_title,
        customer_logged_in=customer_logged_in,
        customer=customer_info,
    )


@bp.route("/logout")
def logout():
    end_customer_session()
    _clear_session_keys(_ADMIN_SESSION_KEYS)
    return redirect("/react/login")


@bp.route("/logout/customer", methods=["POST"])
def logout_customer():
    end_customer_session()
    flash("Logged out of customer portal", "info")
    return redirect("/react/login")


bp.add_url_rule(
    "/login/customer", view_func=login_view, methods=["GET", "POST"], endpoint="customer_login"
)
