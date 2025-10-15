"""HTTP endpoints for the Auth blueprint."""

from __future__ import annotations

from urllib.parse import urljoin, urlparse

from flask import flash, redirect, render_template, request, session, url_for

from app.services.auth_service import admin_auth_service, customer_auth_service

from . import bp

# TODO: Replace with actual auth service once repositories are implemented


def _is_safe_redirect(target: str) -> bool:
    if not target:
        return False
    host_url = request.host_url
    redirect_url = urljoin(host_url, target)
    return urlparse(redirect_url).scheme in {"http", "https"} and redirect_url.startswith(host_url)


def _next_url(default: str = "") -> str:
    target = request.args.get("next") or request.form.get("next") or default
    return target if _is_safe_redirect(target) else default


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Render login page."""
    # For now, just render the template with placeholder data
    # The actual auth logic will be wired up once we have the auth service

    login_title = "Victoria Powder Coating Ltd"
    login_bg_url = ""
    first_run = False  # TODO: Check if any users exist
    customer_logged_in = False  # TODO: Check session
    customer = None

    if request.method == "POST":
        identifier = request.form.get("identifier", "")
        password = request.form.get("password", "")

        # Admin login (username/password) when identifier is not an email
        if identifier and "@" not in identifier:
            admin = admin_auth_service.authenticate_admin(username=identifier, password=password)
            if admin:
                session.clear()
                session["is_admin"] = True
                session["user_id"] = admin.id
                session["me_username"] = admin.username
                flash("Signed in as admin", "success")
                return redirect(_next_url(url_for("dashboard.index")))

        # Customer portal login via email/password
        result = customer_auth_service.authenticate_customer(email=identifier, password=password)
        if result:
            session.clear()
            session["customer_account_id"] = result.account.id
            session["customer_email"] = result.account.email
            flash("Welcome back!", "success")
            return redirect(_next_url(url_for("customer_portal.dashboard")))

        flash("Invalid credentials", "error")

    return render_template(
        "auth/login.html",
        first_run=first_run,
        login_bg_url=login_bg_url,
        login_title=login_title,
        customer_logged_in=customer_logged_in,
        customer=customer,
        next=_next_url(default=""),
    )


@bp.route("/logout")
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))


@bp.route("/logout/customer", methods=["POST"])
def logout_customer():
    """Log out customer and redirect to login."""
    # Clear customer session keys
    session.pop("customer_id", None)
    session.pop("customer_email", None)
    flash("Logged out of customer portal", "info")
    return redirect(url_for("auth.login"))
