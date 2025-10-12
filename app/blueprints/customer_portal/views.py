"""HTTP endpoints for the Customer Portal blueprint."""

from __future__ import annotations

from flask import flash, redirect, render_template, request, session, url_for

from app.services.auth_service import customer_auth_service
from app.services.customer_portal_service import customer_portal_service

from . import bp


@bp.route("/")
@bp.route("/dashboard")
def dashboard():
    """Customer portal dashboard."""
    if not session.get("customer_account_id"):
        flash("Please sign in to access the customer portal", "warning")
        return redirect(url_for("auth.login"))

    account = customer_portal_service.get_account_with_customer(session["customer_account_id"])
    if not account:
        flash("Account not found", "error")
        return redirect(url_for("auth.login"))

    jobs = customer_portal_service.list_jobs_for_account(account.id)
    stats = customer_portal_service.dashboard_stats(account.id)

    return render_template(
        "customer_portal/dashboard.html",
        customer=account.customer if account else None,
        jobs=jobs,
        stats=stats,
    )


@bp.route("/jobs")
def jobs_list():
    """List all customer jobs."""
    if not session.get("customer_account_id"):
        flash("Please sign in to access the customer portal", "warning")
        return redirect(url_for("auth.login"))

    search_query = request.args.get("search", "") or None
    status_filter = request.args.get("status", "") or None

    account = customer_portal_service.get_account_with_customer(session["customer_account_id"])
    if not account:
        flash("Account not found", "error")
        return redirect(url_for("auth.login"))

    jobs = customer_portal_service.list_jobs_for_account(
        account.id,
        search=search_query,
        status=status_filter,
    )

    return render_template(
        "customer_portal/jobs_list.html",
        customer=account.customer if account else None,
        jobs=jobs,
        search_query=search_query or "",
        status_filter=status_filter or "",
    )


@bp.route("/jobs/<int:job_id>")
def job_detail(job_id: int):
    """View job details."""
    if not session.get("customer_account_id"):
        flash("Please sign in to view jobs", "warning")
        return redirect(url_for("auth.login"))

    account = customer_portal_service.get_account_with_customer(session["customer_account_id"])
    if not account:
        flash("Account not found", "error")
        return redirect(url_for("auth.login"))

    job = customer_portal_service.get_job(account.id, job_id)
    if not job:
        flash("Job not found", "error")
        return redirect(url_for("customer_portal.jobs_list"))

    edit_history = []  # TODO: Load from repository

    return render_template(
        "customer_portal/job_detail.html",
        customer=account.customer,
        job=job,
        edit_history=edit_history,
    )


@bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id: int):
    """Edit customer job."""
    if not session.get("customer_account_id"):
        flash("Please sign in to edit jobs", "warning")
        return redirect(url_for("auth.login"))

    account = customer_portal_service.get_account_with_customer(session["customer_account_id"])
    if not account:
        flash("Account not found", "error")
        return redirect(url_for("auth.login"))

    job = customer_portal_service.get_job(account.id, job_id)
    if not job:
        flash("Job not found", "error")
        return redirect(url_for("customer_portal.jobs_list"))

    if request.method == "POST":
        form = request.form
        updated = customer_portal_service.update_customer_job(
            account.id,
            job_id,
            contact_name=form.get("contact_name"),
            phone=form.get("phone"),
            email=form.get("email"),
            po=form.get("po"),
            type=form.get("type"),
            priority=form.get("priority"),
            blast=form.get("blast"),
            prep=form.get("prep"),
            color=form.get("color"),
            description=form.get("description"),
            notes=form.get("notes"),
            due_by=form.get("due_by") or None,
        )
        if updated:
            flash("Job updated successfully", "success")
            return redirect(url_for("customer_portal.job_detail", job_id=job_id))
        flash("Unable to update job", "error")

    return render_template(
        "customer_portal/job_edit.html",
        customer=account.customer,
        job=job,
    )


@bp.route("/jobs/submit", methods=["GET", "POST"])
def submit_job():
    """Submit new job."""
    if not session.get("customer_account_id"):
        flash("Please sign in to submit jobs", "warning")
        return redirect(url_for("auth.login"))

    account = customer_portal_service.get_account_with_customer(session["customer_account_id"])
    if not account:
        flash("Account not found", "error")
        return redirect(url_for("auth.login"))

    customer = account.customer if account else None

    if request.method == "POST":
        form = request.form
        try:
            customer_portal_service.create_customer_job(
                account.id,
                contact_name=form.get("contact_name", ""),
                company=form.get("company", ""),
                phone=form.get("phone"),
                email=form.get("email"),
                po=form.get("po"),
                type=form.get("type"),
                priority=form.get("priority"),
                blast=form.get("blast"),
                prep=form.get("prep"),
                color=form.get("color"),
                description=form.get("description", ""),
                notes=form.get("notes"),
                due_by=form.get("due_by") or None,
            )
        except ValueError as error:
            flash(str(error), "error")
        else:
            flash("Job submitted successfully!", "success")
            return redirect(url_for("customer_portal.dashboard"))

    return render_template(
        "customer_portal/job_submit.html",
        customer=customer,
    )


@bp.route("/profile", methods=["GET", "POST"])
def profile():
    """View/edit customer profile."""
    if not session.get("customer_account_id"):
        flash("Please sign in to view your profile", "warning")
        return redirect(url_for("auth.login"))

    account = customer_portal_service.get_account_with_customer(session["customer_account_id"])
    if not account:
        flash("Account not found", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        form = request.form
        updated = customer_portal_service.update_account(
            account.id,
            first_name=form.get("first_name", account.first_name),
            last_name=form.get("last_name", account.last_name),
            company_name=form.get("company_name"),
            phone=form.get("phone"),
            address=form.get("address"),
        )
        if updated:
            flash("Profile updated successfully", "success")
            return redirect(url_for("customer_portal.profile"))
        flash("Unable to update profile", "error")

    return render_template(
        "customer_portal/profile.html",
        customer=account.customer,
    )


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Register new customer account."""
    if request.method == "POST":
        form = request.form
        password = form.get("password", "")
        confirm_password = form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match", "error")
        else:
            try:
                customer_auth_service.register_customer_account(
                    email=form.get("email", ""),
                    password=password,
                    first_name=form.get("first_name", ""),
                    last_name=form.get("last_name", ""),
                    company_name=form.get("company_name"),
                    phone=form.get("phone"),
                )
            except ValueError as error:
                flash(str(error), "error")
            else:
                flash("Account created! Please sign in.", "success")
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
    session.pop("customer_account_id", None)
    session.pop("customer_email", None)
    flash("Logged out of customer portal", "info")
    return redirect(url_for("auth.login"))


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Forgot password flow."""
    # TODO: Implement password reset
    flash("Password reset functionality pending migration", "info")
    return redirect(url_for("auth.login"))
