"""HTTP endpoints for the Intake blueprint."""

from flask import flash, redirect, render_template, request, url_for

from app.services.jobs_service import job_intake_service
from app.services.options_service import options_service
from app.services.upload_service import save_job_files

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
                date_in=form.get("dateIn"),
                due_by=form.get("dueBy"),
                po=form.get("po"),
                category=form.get("category"),
                blast=form.get("blast"),
                priority=form.get("priority"),
                prep=form.get("prep"),
                color=form.get("color"),
                color_source=form.get("color_source"),
                intake_source=form.get("intake_source") or "production",
            )
        except ValueError as error:
            flash(str(error), "error")
            return render_template(
                "intake/form.html",
                form_data=form,
                form_options=options_service.get_job_form_options(),
            )
        else:
            # After job is created, persist any uploaded files and link as photos
            files = request.files.getlist("photos") or []
            if files:
                saved = save_job_files(job.id, job.company, files)
                # Record in repository via jobs blueprint conventions
                from app.repositories import job_repo  # local import to avoid cycles

                for rel_path, orig in saved:
                    job_repo.add_photo(job.id, filename=rel_path, original_name=orig)

            flash("Production intake submitted successfully.", "success")
            return redirect(url_for("jobs.detail", job_id=job.id))

    return render_template(
        "intake/form.html",
        form_data={},
        form_options=options_service.get_job_form_options(),
    )


@bp.route("/railing", methods=["GET", "POST"])
def railing_intake():
    """Railing-specific intake form."""
    if request.method == "POST":
        form = request.form
        try:
            # Map railing form to production fields plus measurements appended in notes
            notes = form.get("notes") or ""
            sections_text = form.get("sections_text") or ""
            if sections_text:
                notes = (notes or "") + "\n" + sections_text

            job = job_intake_service.create_production_job(
                contact_name=form.get("contact_name", ""),
                company=form.get("company", ""),
                phone=form.get("phone"),
                email=form.get("email"),
                description=form.get("description", ""),
                notes=notes,
                date_in=form.get("dateIn"),
                due_by=form.get("dueBy"),
                po=form.get("po"),
                category="Railing",
                blast=form.get("blast"),
                priority=form.get("priority"),
                prep=form.get("prep"),
                color=form.get("color"),
                color_source=None,
                intake_source="railing",
            )
        except ValueError as error:
            flash(str(error), "error")
            return render_template("intake/railing.html", form_data=form)
        else:
            files = request.files.getlist("photos") or []
            if files:
                saved = save_job_files(job.id, job.company, files)
                from app.repositories import job_repo  # local import

                for rel_path, orig in saved:
                    job_repo.add_photo(job.id, filename=rel_path, original_name=orig)

            flash("Railing intake submitted successfully.", "success")
            return redirect(url_for("jobs.detail", job_id=job.id))

    return render_template("intake/railing.html", form_data={})
