"""HTTP endpoints for the Auth blueprint."""

from __future__ import annotations

from flask import flash, redirect, render_template, request, session, url_for

from app.services.auth_service import customer_auth_service

from . import bp

# TODO: Replace with actual auth service once repositories are implemented


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

        result = customer_auth_service.authenticate_customer(email=identifier, password=password)
        if result:
            session["customer_account_id"] = result.account.id
            session["customer_email"] = result.account.email
            flash("Welcome back!", "success")
            return redirect(url_for("customer_portal.dashboard"))

        flash("Invalid email or password", "error")

    return render_template(
        "auth/login.html",
        first_run=first_run,
        login_bg_url=login_bg_url,
        login_title=login_title,
        customer_logged_in=customer_logged_in,
        customer=customer,
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
