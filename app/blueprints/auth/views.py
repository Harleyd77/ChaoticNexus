"""HTTP endpoints for the Auth blueprint."""

from __future__ import annotations

from flask import flash, redirect, render_template, request, session, url_for

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
        # Placeholder - redirect to dashboard for now
        flash("Login functionality pending migration", "info")
        return redirect(url_for("dashboard.index"))

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
