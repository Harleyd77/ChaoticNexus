"""
Customer Portal Job Management

Handles job viewing, editing, and submission for customers.
"""

from datetime import datetime
from flask import flash, redirect, render_template, request, url_for

from . import customer_portal_bp
from ...core.db import get_db
from .auth import require_customer_login


@customer_portal_bp.route("/jobs")
@require_customer_login
def jobs_list(customer):
    """List all customer's jobs."""
    db = get_db()

    # Get filter parameters
    status_filter = request.args.get("status", "")
    search_query = request.args.get("search", "")

    # Build query
    query = """
        SELECT j.*, c.company as customer_company
        FROM jobs j
        LEFT JOIN customer_accounts ca ON j.customer_account_id = ca.id
        LEFT JOIN customers c ON ca.company_name = c.company
        WHERE j.customer_account_id = ?
    """
    params = [customer["id"]]

    if status_filter:
        query += " AND j.status = ?"
        params.append(status_filter)

    if search_query:
        query += " AND (j.description LIKE ? OR j.po LIKE ? OR j.contact_name LIKE ?)"
        search_pattern = f"%{search_query}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    query += " ORDER BY j.created_at DESC"

    jobs = db.execute(query, params).fetchall()

    return render_template("customer_portal/jobs_list.html",
                         customer=customer,
                         jobs=jobs,
                         status_filter=status_filter,
                         search_query=search_query)


@customer_portal_bp.route("/jobs/<int:job_id>")
@require_customer_login
def job_detail(customer, job_id):
    """View job details."""
    db = get_db()

    job = db.execute("""
        SELECT j.*, c.company as customer_company,
               COUNT(jh.id) as edit_count
        FROM jobs j
        LEFT JOIN customer_accounts ca ON j.customer_account_id = ca.id
        LEFT JOIN customers c ON ca.company_name = c.company
        LEFT JOIN job_edit_history jh ON j.id = jh.job_id
        WHERE j.id = ? AND j.customer_account_id = ?
        GROUP BY j.id, j.created_at, j.date_in, j.due_by, j.contact_name, j.company, 
                 j.phone, j.email, j.po, j.type, j.priority, j.blast, j.prep, j.color, 
                 j.color_source, j.description, j.notes, j.status, j.department, 
                 j.completed_at, j.work_order_json, j.archived, j.archived_reason, 
                 j.order_index, j.on_screen, j.screen_order_index, j.customer_account_id, 
                 j.submitted_by_customer, j.requires_approval, c.company
    """, (job_id, customer["id"])).fetchone()

    if not job:
        flash("Job not found or access denied", "error")
        return redirect(url_for("customer_portal.dashboard"))

    # Get edit history
    edit_history = db.execute("""
        SELECT jh.*, ca.first_name, ca.last_name
        FROM job_edit_history jh
        LEFT JOIN customer_accounts ca ON jh.customer_id = ca.id
        WHERE jh.job_id = ?
        ORDER BY jh.created_at DESC
    """, (job_id,)).fetchall()

    return render_template("customer_portal/job_detail.html",
                         customer=customer,
                         job=job,
                         edit_history=edit_history)


@customer_portal_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@require_customer_login
def edit_job(customer, job_id):
    """Edit job details."""
    db = get_db()

    # Get job (ensure it belongs to customer)
    job = db.execute("""
        SELECT * FROM jobs WHERE id = ? AND customer_account_id = ?
    """, (job_id, customer["id"])).fetchone()

    if not job:
        flash("Job not found or access denied", "error")
        return redirect(url_for("customer_portal.dashboard"))

    if request.method == "POST":
        # Get form data
        contact_name = request.form.get("contact_name", "").strip()
        company = request.form.get("company", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        po = request.form.get("po", "").strip()
        description = request.form.get("description", "").strip()
        notes = request.form.get("notes", "").strip()
        due_by = request.form.get("due_by", "").strip()
        change_reason = request.form.get("change_reason", "").strip()

        # Basic validation
        errors = []
        if not contact_name:
            errors.append("Contact name is required")
        if not description:
            errors.append("Description is required")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("customer_portal/job_edit.html",
                                 customer=customer,
                                 job=job)

        # Track changes
        changes = []
        fields_to_track = {
            "contact_name": job["contact_name"],
            "company": job["company"],
            "phone": job["phone"],
            "email": job["email"],
            "po": job["po"],
            "description": job["description"],
            "notes": job["notes"],
            "due_by": job["due_by"]
        }

        for field, old_value in fields_to_track.items():
            new_value = locals()[field]
            if old_value != new_value:
                changes.append({
                    "field": field,
                    "old_value": old_value,
                    "new_value": new_value
                })

        # Update job
        db.execute("""
            UPDATE jobs
            SET contact_name = ?, company = ?, phone = ?, email = ?,
                po = ?, description = ?, notes = ?, due_by = ?
            WHERE id = ?
        """, (contact_name, company, phone, email, po, description, notes, due_by, job_id))

        # Record changes
        for change in changes:
            db.execute("""
                INSERT INTO job_edit_history
                (job_id, customer_id, field_name, old_value, new_value, change_reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (job_id, customer["id"], change["field"], change["old_value"],
                  change["new_value"], change_reason))

        db.commit()

        flash("Job updated successfully!", "success")
        return redirect(url_for("customer_portal.job_detail", job_id=job_id))

    return render_template("customer_portal/job_edit.html",
                         customer=customer,
                         job=job)


@customer_portal_bp.route("/jobs/submit", methods=["GET", "POST"])
@require_customer_login
def submit_job(customer):
    """Submit a new job."""
    if request.method == "POST":
        # Get form data
        contact_name = request.form.get("contact_name", "").strip()
        company = request.form.get("company", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        po = request.form.get("po", "").strip()
        job_type = request.form.get("type", "").strip()
        priority = request.form.get("priority", "Normal").strip()
        blast = request.form.get("blast", "").strip()
        prep = request.form.get("prep", "").strip()
        color = request.form.get("color", "").strip()
        description = request.form.get("description", "").strip()
        notes = request.form.get("notes", "").strip()
        due_by = request.form.get("due_by", "").strip()

        # Validation
        errors = []
        if not contact_name:
            errors.append("Contact name is required")
        if not company:
            errors.append("Company name is required")
        if not description:
            errors.append("Job description is required")
        if not job_type:
            errors.append("Job type is required")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("customer_portal/job_submit.html",
                                 customer=customer)

        # Create job
        db = get_db()
        db.execute("""
            INSERT INTO jobs
            (created_at, contact_name, company, phone, email, po, type, priority,
             blast, prep, color, description, notes, due_by, customer_account_id,
             submitted_by_customer, requires_approval, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now(), contact_name, company, phone, email, po, job_type,
              priority, blast, prep, color, description, notes, due_by,
              customer["id"], True, True, "Pending Approval"))

        db.commit()

        flash("Job submitted successfully! We'll review it and get back to you soon.", "success")
        return redirect(url_for("customer_portal.dashboard"))

    return render_template("customer_portal/job_submit.html", customer=customer)
