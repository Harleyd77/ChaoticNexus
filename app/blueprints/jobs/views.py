"""HTTP endpoints for Jobs blueprint."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from flask import Response, flash, redirect, render_template, request, url_for

from app.repositories import job_repo

from . import bp

_KANBAN_COLUMNS: list[dict[str, str | bool]] = [
    {"key": "intake", "label": "Intake Queue", "timer": False},
    {"key": "prep", "label": "Prep & Masking", "timer": True},
    {"key": "coating", "label": "Coating Booth", "timer": True},
    {"key": "qa", "label": "Quality Review", "timer": False},
    {"key": "completed", "label": "Ready / Completed", "timer": False},
]

_FORM_OPTIONS = {
    "category": ["Production", "Architectural", "Industrial", "Custom"],
    "priority": ["Critical", "High", "Normal", "Low"],
    "blast": ["None", "Mechanical", "Chemical"],
    "prep": ["TBD", "Wipe down", "Mask only", "Mask + Hang", "Degrease"],
}

_DEPARTMENTS = [
    ("intake", "Intake Queue"),
    ("prep", "Prep & Masking"),
    ("coating", "Coating Booth"),
    ("qa", "Quality Review"),
    ("completed", "Ready / Completed"),
    ("shipping", "Shipping / Pickup"),
]


def _group_jobs_by_department(jobs: Sequence) -> dict[str, list]:
    grouped: dict[str, list] = {col["key"]: [] for col in _KANBAN_COLUMNS}
    for job in jobs:
        department = getattr(job, "department", None) or "intake"
        grouped.setdefault(department, []).append(job)
    return grouped


@bp.get("/")
def index():
    """Render the jobs index view."""
    search_query = request.args.get("q", "").strip() or None
    jobs = job_repo.list_jobs(query=search_query)
    metrics = {
        "active": sum(1 for job in jobs if (job.department or "").lower() != "completed"),
        "due_today": sum(1 for job in jobs if job.due_by and job.due_by == date.today()),
        "awaiting_pickup": sum(
            1 for job in jobs if (job.department or "").lower() == "completed" and job.completed_at
        ),
    }
    filters = {
        "query": search_query or "",
        "stage": "all",
        "show_archived": False,
    }
    return render_template(
        "jobs/index.html",
        jobs=jobs,
        metrics=metrics,
        filters=filters,
    )


@bp.route("/new", methods=["GET", "POST"])
def new_job():
    """Render a simple form to create a job without placeholders."""
    if request.method == "POST":
        company = request.form.get("company", "").strip()
        description = request.form.get("description", "").strip()
        contact_name = request.form.get("contact_name", "").strip() or None

        errors = []
        if not company:
            errors.append("Company name is required.")
        if not description:
            errors.append("Description is required.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "jobs/new.html",
                form_data={
                    "company": company,
                    "contact_name": request.form.get("contact_name", ""),
                    "description": description,
                },
            )

        job = job_repo.create_job(
            company=company,
            contact_name=contact_name,
            description=description,
        )
        flash(f"Job #{job.id} created", "success")
        return redirect(url_for("jobs.detail", job_id=job.id))

    return render_template("jobs/new.html", form_data={})


@bp.get("/export")
def export_csv() -> Response:
    """Export job data as CSV (basic implementation)."""
    jobs = job_repo.list_jobs()
    header = "id,company,status,due_by\n"
    rows = [f"{job.id},{job.company or ''},{job.status or ''},{job.due_by or ''}" for job in jobs]
    csv_content = header + "\n".join(rows)
    return Response(
        csv_content,
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment; filename=jobs.csv",
        },
    )


@bp.get("/kanban")
def kanban():
    """Render the jobs kanban board."""
    jobs = job_repo.list_jobs()
    columns = _group_jobs_by_department(jobs)
    filters = {
        "search": "",
        "color": "",
        "status": "",
    }
    color_options = sorted({job.color for job in jobs if job.color})
    status_options = sorted({job.status for job in jobs if job.status})
    return render_template(
        "jobs/kanban.html",
        columns_meta=_KANBAN_COLUMNS,
        columns=columns,
        filters=filters,
        color_options=color_options,
        status_options=status_options,
    )


def _find_job(job_id: int):
    return job_repo.get_job(job_id)


@bp.get("/<int:job_id>/")
def detail(job_id: int):
    """Render the job detail view."""
    job = _find_job(job_id)
    if not job:
        return (
            render_template(
                "errors/error.html",
                error="Job Not Found",
                message="We couldn't locate that job. It may have been archived.",
            ),
            404,
        )

    photos = [
        {
            "url": photo.filename,
            "label": photo.original_name or "Job photo",
        }
        for photo in getattr(job, "photos", [])
    ]
    time_logs = job_repo.list_time_logs(job.id)
    powder_usage = job_repo.list_powder_usage(job.id)
    total_minutes = sum(filter(None, (log.minutes for log in time_logs)))
    total_powder = sum(filter(None, (usage.amount_used for usage in powder_usage)))
    return render_template(
        "jobs/detail.html",
        job=job,
        photos=photos,
        time_logs=time_logs,
        powder_usage=powder_usage,
        total_minutes=total_minutes,
        total_powder=total_powder,
        is_admin=True,
    )


@bp.get("/<int:job_id>/edit")
def edit(job_id: int):
    """Render the job edit form (placeholder)."""
    job = _find_job(job_id)
    if not job:
        return (
            render_template(
                "errors/error.html",
                error="Job Not Found",
                message="We couldn't locate that job. It may have been archived.",
            ),
            404,
        )

    photos = [
        {
            "url": photo.filename,
            "label": photo.original_name or "Job photo",
        }
        for photo in getattr(job, "photos", [])
    ]
    return render_template(
        "jobs/edit.html",
        job=job,
        photos=photos,
        form_options=_FORM_OPTIONS,
        departments=_DEPARTMENTS,
        is_admin=True,
    )
