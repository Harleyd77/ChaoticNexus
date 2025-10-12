"""HTTP endpoints for the Customer Portal blueprint."""

from __future__ import annotations

from datetime import date, timedelta

from flask import flash, redirect, render_template, request, url_for

from . import bp

# TODO: Replace with actual customer service once repositories are implemented


def _sample_customer():
    """Placeholder customer data."""
    return {
        "id": 1,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "company_name": "Acme Industries",
        "phone": "250-555-0123",
        "address": "123 Main St, Victoria, BC",
        "email_verified": True,
        "created_at": date(2024, 1, 15),
        "last_login": date.today(),
        "job_count": 12,
        "completed_jobs": 8,
        "pending_jobs": 4,
    }


def _sample_jobs():
    """Placeholder job data for customer portal."""
    today = date.today()
    return [
        {
            "id": 1042,
            "customer_account_id": 1,
            "contact_name": "Jane Doe",
            "company": "Acme Industries",
            "phone": "250-555-0123",
            "email": "jane@example.com",
            "po": "PO-4587",
            "type": "Powder Coating",
            "priority": "Normal",
            "blast": "Medium",
            "prep": "Wash",
            "color": "RAL 9005 - Jet Black",
            "description": "Exterior railings (200 ft). Request matte finish.",
            "notes": "Customer prefers pickup on Friday.",
            "status": "In Progress",
            "due_by": (today + timedelta(days=3)).isoformat(),
            "created_at": (today - timedelta(days=5)).isoformat(),
            "submitted_by_customer": True,
        },
        {
            "id": 1038,
            "customer_account_id": 1,
            "contact_name": "Jane Doe",
            "company": "Acme Industries",
            "phone": "250-555-0123",
            "email": "jane@example.com",
            "po": "PO-4501",
            "type": "Sandblasting",
            "priority": "Normal",
            "blast": "Heavy",
            "prep": "Media Blast",
            "color": "",
            "description": "Aluminum panels – ensure even coverage on edges.",
            "notes": "",
            "status": "Ready for Pickup",
            "due_by": today.isoformat(),
            "created_at": (today - timedelta(days=12)).isoformat(),
            "submitted_by_customer": True,
        },
        {
            "id": 1021,
            "customer_account_id": 1,
            "contact_name": "Jane Doe",
            "company": "Acme Industries",
            "phone": "250-555-0123",
            "email": "jane@example.com",
            "po": "PO-4388",
            "type": "Powder Coating",
            "priority": "Rush",
            "blast": "Light",
            "prep": "Wash",
            "color": "Custom Bronze Match",
            "description": "Gate hardware, 50 units.",
            "notes": "Sample approved on 10/01.",
            "status": "Pending Approval",
            "due_by": (today + timedelta(days=7)).isoformat(),
            "created_at": (today - timedelta(days=2)).isoformat(),
            "submitted_by_customer": True,
        },
    ]


@bp.route("/")
@bp.route("/dashboard")
def dashboard():
    """Customer portal dashboard."""
    customer = _sample_customer()
    jobs = _sample_jobs()

    stats = {
        "total": len(jobs),
        "pending": len(
            [j for j in jobs if j["status"] in ["In Progress", "Not Started", "Pending Approval"]]
        ),
        "completed": len([j for j in jobs if j["status"] == "Completed"]),
        "overdue": 0,  # TODO: Calculate from due dates
    }

    return render_template(
        "customer_portal/dashboard.html",
        customer=customer,
        jobs=jobs,
        stats=stats,
    )


@bp.route("/jobs")
def jobs_list():
    """List all customer jobs."""
    customer = _sample_customer()
    jobs = _sample_jobs()

    search_query = request.args.get("search", "")
    status_filter = request.args.get("status", "")

    # TODO: Apply actual filters once repository exists

    return render_template(
        "customer_portal/jobs_list.html",
        customer=customer,
        jobs=jobs,
        search_query=search_query,
        status_filter=status_filter,
    )


@bp.route("/jobs/<int:job_id>")
def job_detail(job_id: int):
    """View job details."""
    customer = _sample_customer()
    jobs = _sample_jobs()
    job = next((j for j in jobs if j["id"] == job_id), None)

    if not job:
        flash("Job not found", "error")
        return redirect(url_for("customer_portal.jobs_list"))

    edit_history = []  # TODO: Load from repository

    return render_template(
        "customer_portal/job_detail.html",
        customer=customer,
        job=job,
        edit_history=edit_history,
    )


@bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id: int):
    """Edit customer job."""
    customer = _sample_customer()
    jobs = _sample_jobs()
    job = next((j for j in jobs if j["id"] == job_id), None)

    if not job:
        flash("Job not found", "error")
        return redirect(url_for("customer_portal.jobs_list"))

    if request.method == "POST":
        # TODO: Save changes via repository
        flash("Job updated successfully", "success")
        return redirect(url_for("customer_portal.job_detail", job_id=job_id))

    return render_template(
        "customer_portal/job_edit.html",
        customer=customer,
        job=job,
    )


@bp.route("/jobs/submit", methods=["GET", "POST"])
def submit_job():
    """Submit new job."""
    customer = _sample_customer()

    if request.method == "POST":
        # TODO: Create job via repository
        flash("Job submitted successfully", "success")
        return redirect(url_for("customer_portal.dashboard"))

    return render_template(
        "customer_portal/job_submit.html",
        customer=customer,
    )


@bp.route("/profile", methods=["GET", "POST"])
def profile():
    """View/edit customer profile."""
    customer = _sample_customer()

    if request.method == "POST":
        # TODO: Update profile via repository
        flash("Profile updated successfully", "success")
        return redirect(url_for("customer_portal.profile"))

    return render_template(
        "customer_portal/profile.html",
        customer=customer,
    )


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Register new customer account."""
    if request.method == "POST":
        # TODO: Create account via repository
        flash("Account created successfully! Please check your email to verify.", "success")
        return redirect(url_for("auth.login"))

    return render_template(
        "customer_portal/register.html",
        first_name=request.form.get("first_name", ""),
        last_name=request.form.get("last_name", ""),
        email=request.form.get("email", ""),
        company_name=request.form.get("company_name", ""),
        phone=request.form.get("phone", ""),
    )


@bp.route("/logout")
def logout():
    """Log out customer."""
    return redirect(url_for("auth.logout_customer"))


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Forgot password flow."""
    # TODO: Implement password reset
    flash("Password reset functionality pending migration", "info")
    return redirect(url_for("auth.login"))
