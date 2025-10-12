"""Customer portal authentication blueprint."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import generate_password_hash

# Import the blueprint (defined in __init__.py)
from . import customer_portal_bp
from ...core.db import get_db
from ...core.customer_auth import end_customer_session
from ...core.customers import normalize_company
from ...core.security import public_endpoint


@customer_portal_bp.route("/register", methods=["GET", "POST"])
@public_endpoint
def register():
    """Customer registration page."""
    import sys
    print("DEBUG: Customer register route handler called", file=sys.stderr)
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        company_name = request.form.get("company_name", "").strip()
        phone = request.form.get("phone", "").strip()

        errors = []

        if not email:
            errors.append("Email is required")
        elif "@" not in email:
            errors.append("Please enter a valid email address")

        if not password:
            errors.append("Password is required")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        elif not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        elif not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")

        if password != confirm_password:
            errors.append("Passwords do not match")

        if not first_name:
            errors.append("First name is required")

        if not last_name:
            errors.append("Last name is required")

        db = get_db()
        existing_customer = db.execute(
            "SELECT id FROM customer_accounts WHERE email = ?",
            (email,),
        ).fetchone()

        if existing_customer:
            errors.append("An account with this email already exists")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "customer_portal/register.html",
                email=email,
                first_name=first_name,
                last_name=last_name,
                company_name=company_name,
                phone=phone,
            )

        password_hash = generate_password_hash(password)
        now = datetime.now()
        now_iso = now.isoformat()
        db.execute(
            """
            INSERT INTO customer_accounts
            (email, password_hash, first_name, last_name, company_name, phone, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (email, password_hash, first_name, last_name, company_name, phone, now, now),
        )

        full_name = f"{first_name} {last_name}".strip()
        company_normalized = normalize_company(company_name) or normalize_company(full_name)
        if company_normalized:
            existing_row = db.execute(
                "SELECT id FROM customers WHERE lower(trim(company)) = lower(trim(?))",
                (company_normalized,),
            ).fetchone()
            if existing_row:
                db.execute(
                    """
                    UPDATE customers
                       SET company = ?, contact_name = ?, phone = ?, email = ?, updated_at = ?
                     WHERE id = ?
                    """,
                    (company_normalized, full_name, phone, email, now_iso, existing_row["id"]),
                )
            else:
                db.execute(
                    """
                    INSERT INTO customers (company, contact_name, phone, email, address, notes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, '', '', ?, ?)
                    """,
                    (company_normalized, full_name, phone, email, now_iso, now_iso),
                )

        db.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("customer_portal/register.html")


@customer_portal_bp.route("/forgot-password", methods=["GET", "POST"])
@public_endpoint
def forgot_password():
    """Password reset request."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Email is required", "error")
            return render_template("customer_portal/forgot_password.html")

        db = get_db()
        customer = db.execute(
            "SELECT id, first_name FROM customer_accounts WHERE email = ?",
            (email,),
        ).fetchone()

        if customer:
            flash("Password reset instructions have been sent to your email", "success")
        else:
            flash("If an account with that email exists, password reset instructions have been sent", "info")

        return redirect(url_for("auth.login"))

    return render_template("customer_portal/forgot_password.html")


@customer_portal_bp.route("/logout")
def logout():
    """Log out the customer and redirect to login."""
    end_customer_session()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


def get_current_customer():
    """Get the currently logged-in customer."""
    customer_id = session.get("customer_id")
    session_token = session.get("customer_session_token")

    if not customer_id or not session_token:
        return None

    db = get_db()
    customer = db.execute(
        """
        SELECT ca.*, cs.expires_at
        FROM customer_accounts ca
        JOIN customer_sessions cs ON ca.id = cs.customer_id
        WHERE ca.id = ?
          AND cs.session_token = ?
          AND cs.is_active = TRUE
          AND cs.expires_at > NOW()
    """,
        (customer_id, session_token),
    ).fetchone()

    return customer


def require_customer_login(f):
    """Decorator to require customer authentication."""
    def decorated_function(*args, **kwargs):
        customer = get_current_customer()
        if not customer:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(customer, *args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function
