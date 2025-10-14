"""HTTP endpoints for the Customer Portal blueprint."""

from __future__ import annotations

from flask import current_app, flash, redirect, render_template, request, session, url_for

from app.services.auth_service import customer_auth_service
from app.services.customer_portal_service import customer_portal_service

from . import bp

_LANDING_FEATURES: list[dict[str, str]] = [
    {
        "title": "Track job progress",
        "description": (
            "View real-time status updates, stage changes, and pickup "
            "notifications for every job you submit."
        ),
        "icon": "clipboard",
    },
    {
        "title": "Share project details",
        "description": (
            "Update notes, upload instructions, and keep your contact "
            "information current without calling the shop."
        ),
        "icon": "chat",
    },
    {
        "title": "Submit new work",
        "description": (
            "Launch production or railing intake forms from anywhere—"
            "requests drop straight into the coating workflow."
        ),
        "icon": "sparkles",
    },
]

_LANDING_STEPS: list[dict[str, str]] = [
    {
        "number": "01",
        "title": "Create your account",
        "description": (
            "Register with your business email so we can link jobs to the "
            "right customer record immediately."
        ),
    },
    {
        "number": "02",
        "title": "Submit or review jobs",
        "description": (
            "Send new work orders or review active jobs with live status, "
            "notes, and expected completion dates."
        ),
    },
    {
        "number": "03",
        "title": "Stay informed",
        "description": (
            "Receive updates as jobs move through intake, prep, coating, "
            "QA, and pickup—all from one dashboard."
        ),
    },
]


def _get_current_account():
    account_id = session.get("customer_account_id")
    if not account_id:
        return None
    return customer_portal_service.get_account_with_customer(account_id)


@bp.get("/portal")
def portal_redirect():
    """Legacy path alias: /customer/portal → customer landing page."""
    return home()


@bp.route("/", methods=["GET", "POST"])
def home():
    """Public landing page for the customer portal."""
    account = _get_current_account()
    support_email = (
        current_app.config.get("BRANDING_SUPPORT_EMAIL") or "support@victoriapowdercoating.com"
    )
    phone = current_app.config.get("BRANDING_SUPPORT_PHONE") or "(250) 555-0133"

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            flash("Enter an email and we'll reach out shortly.", "error")
        else:
            # TODO: Hook into CRM / ticket system. For now, reuse flash messaging.
            flash("Thanks! We'll follow up within one business day.", "success")
        return redirect(url_for("customer_portal.home"))

    if account:
        destination = request.args.get("next") or request.args.get("redirect")
        if destination == "jobs":
            return redirect(url_for("customer_portal.jobs_list"))
        if destination == "profile":
            return redirect(url_for("customer_portal.profile"))
        return redirect(url_for("customer_portal.dashboard"))

    return render_template(
        "customer_portal/landing.html",
        account=None,
        customer=None,
        features=_LANDING_FEATURES,
        steps=_LANDING_STEPS,
        login_url=url_for("auth.login"),
        register_url=url_for("customer_portal.register"),
        support_email=support_email,
        support_phone=phone,
    )


@bp.get("/dashboard")
def dashboard():
    """Customer portal dashboard."""
    account = _get_current_account()
    if not account:
        flash("Please sign in to access the customer portal", "warning")
        return redirect(url_for("auth.login", next=request.path))

    recent_jobs = customer_portal_service.list_recent_jobs(account.id, limit=5)
    stats = customer_portal_service.dashboard_stats(account.id)
    summary = customer_portal_service.customer_summary(account.id)

    return render_template(
        "customer_portal/dashboard.html",
        account=account,
        customer=account.customer if account else None,
        jobs=recent_jobs,
        stats=stats,
        summary=summary,
    )


@bp.route("/jobs")
def jobs_list():
    """List all customer jobs."""
    account = _get_current_account()
    if not account:
        flash("Please sign in to access the customer portal", "warning")
        return redirect(url_for("auth.login", next=request.path))

    search_query = request.args.get("search", "") or None
    status_filter = request.args.get("status", "") or None

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
    account = _get_current_account()
    if not account:
        flash("Please sign in to view jobs", "warning")
        return redirect(url_for("auth.login", next=request.path))

    job = customer_portal_service.get_job(account.id, job_id)
    if not job:
        flash("Job not found", "error")
        return redirect(url_for("customer_portal.jobs_list"))

    edit_history = customer_portal_service.list_job_edit_history(job.id)

    return render_template(
        "customer_portal/job_detail.html",
        customer=account.customer,
        job=job,
        edit_history=edit_history,
    )


@bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id: int):
    """Edit customer job."""
    account = _get_current_account()
    if not account:
        flash("Please sign in to edit jobs", "warning")
        return redirect(url_for("auth.login", next=request.path))

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
    account = _get_current_account()
    if not account:
        flash("Please sign in to submit jobs", "warning")
        return redirect(url_for("auth.login", next=request.path))

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
    account = _get_current_account()
    if not account:
        flash("Please sign in to view your profile", "warning")
        return redirect(url_for("auth.login", next=request.path))

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
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        if email:
            customer_auth_service.initiate_password_reset(email=email)
        flash("If the email exists, a reset link was sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("customer_portal/forgot_password.html")


@bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token") or request.form.get("token")
    if request.method == "POST":
        new_password = request.form.get("password") or ""
        if customer_auth_service.reset_password(token=token or "", new_password=new_password):
            flash("Password updated. Please sign in.", "success")
            return redirect(url_for("auth.login"))
        flash("Invalid or expired token, or weak password.", "error")
    return render_template("customer_portal/reset_password.html", token=token)
