"""HTTP endpoints for the Intake blueprint."""

from flask import flash, redirect, render_template, request, url_for

from app.services.jobs_service import job_intake_service

from . import bp


@bp.route("/form", methods=["GET", "POST"])
def intake_form():
    """Production intake form."""
    if request.method == "POST":
        form = request.form
        try:
            job = job_intake_service.create_production_job(
                contact_name=form.get("contact_name", ""),
                company=form.get("company", ""),
                phone=form.get("phone"),
                email=form.get("email"),
                description=form.get("description", ""),
                notes=form.get("notes"),
            )
        except ValueError as error:
            flash(str(error), "error")
            return render_template("intake/form.html", form_data=form)
        else:
            flash("Production intake submitted successfully.", "success")
            return redirect(url_for("jobs.detail", job_id=job.id))

    return render_template("intake/form.html", form_data={})


@bp.route("/railing", methods=["GET", "POST"])
def railing_intake():
    """Railing-specific intake form."""
    if request.method == "POST":
        form = request.form
        try:
            job = job_intake_service.create_railing_job(
                contact_name=form.get("contact_name", ""),
                company=form.get("company", ""),
                description=form.get("description", ""),
                measurements=form.get("measurements"),
            )
        except ValueError as error:
            flash(str(error), "error")
            return render_template("intake/railing.html", form_data=form)
        else:
            flash("Railing intake submitted successfully.", "success")
            return redirect(url_for("jobs.detail", job_id=job.id))

    return render_template("intake/railing.html", form_data={})
