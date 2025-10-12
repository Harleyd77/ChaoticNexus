"""
Customer Portal Dashboard

Shows customer's jobs and provides navigation to other features.
"""

from datetime import datetime
from flask import flash, redirect, render_template, request, url_for

from . import customer_portal_bp
from ...core.db import get_db
from .auth import require_customer_login


@customer_portal_bp.route("/dashboard")
@require_customer_login
def dashboard(customer):
    """Customer portal dashboard with job statistics and recent jobs."""
    db = get_db()
    
    # Get job statistics for this customer
    stats = db.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'Overdue' THEN 1 ELSE 0 END) as overdue
        FROM jobs 
        WHERE company = ? AND (archived IS NULL OR archived = 0)
    """, (customer['company_name'] or f"{customer['first_name']} {customer['last_name']}",)).fetchone()
    
    # Get recent jobs for this customer
    jobs = db.execute("""
        SELECT id, created_at, description, status, due_by, color, type
        FROM jobs 
        WHERE company = ? AND (archived IS NULL OR archived = 0)
        ORDER BY created_at DESC
        LIMIT 10
    """, (customer['company_name'] or f"{customer['first_name']} {customer['last_name']}",)).fetchall()
    
    return render_template(
        "customer_portal/dashboard.html", 
        customer=customer,
        stats=stats,
        jobs=jobs
    )


@customer_portal_bp.route("/profile")
@require_customer_login
def profile(customer):
    """Customer profile management."""
    return render_template("customer_portal/profile.html", customer=customer)


@customer_portal_bp.route("/profile", methods=["POST"])
@require_customer_login
def update_profile(customer):
    """Update customer profile information."""
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    company_name = request.form.get("company_name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    # Validation
    errors = []
    if not first_name:
        errors.append("First name is required")
    if not last_name:
        errors.append("Last name is required")

    if errors:
        for error in errors:
            flash(error, "error")
        return render_template("customer_portal/profile.html", customer=customer)

    # Update profile
    db = get_db()
    db.execute("""
        UPDATE customer_accounts
        SET first_name = ?, last_name = ?, company_name = ?, phone = ?, address = ?, updated_at = ?
        WHERE id = ?
    """, (first_name, last_name, company_name, phone, address, datetime.now(), customer["id"]))
    db.commit()

    flash("Profile updated successfully!", "success")
    return redirect(url_for("customer_portal.profile"))
