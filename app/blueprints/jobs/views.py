"""HTTP endpoints for Jobs blueprint."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from flask import Response, flash, jsonify, redirect, render_template, request, url_for

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

_STATUS_OPTIONS = [
    "Intake",
    "Pending Approval",
    "Not Started",
    "In Progress",
    "Ready for Pickup",
    "Completed",
]


def _group_jobs_by_department(jobs: Sequence) -> dict[str, list]:
    grouped: dict[str, list] = {col["key"]: [] for col in _KANBAN_COLUMNS}
    for job in jobs:
        department = getattr(job, "department", None) or "intake"
        grouped.setdefault(department, []).append(job)
    return grouped


def _job_to_form_data(job) -> dict[str, str]:
    return {
        "contact_name": job.contact_name or "",
        "phone": job.phone or "",
        "email": job.email or "",
        "company": job.company or "",
        "po": job.po or "",
        "type": job.type or "",
        "priority": job.priority or "",
        "blast": job.blast or "",
        "prep": job.prep or "",
        "color": job.color or job.coating or "",
        "status": job.status or "",
        "department": job.department or "",
        "date_in": job.date_in.isoformat() if job.date_in else "",
        "due_by": job.due_by.isoformat() if job.due_by else "",
        "description": job.description or "",
        "notes": job.notes or "",
    }


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


@bp.get("/../jobs.csv")
def legacy_jobs_csv() -> Response:
    """Legacy CSV path for jobs: /jobs.csv

    Keep functioning during parity; delegate to the canonical exporter.
    """
    return export_csv()


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


@bp.get("/screen")
def screen_view():
    jobs = [j for j in job_repo.list_jobs() if getattr(j, "on_screen", False)]
    return render_template(
        "jobs/kanban.html",
        columns_meta=_KANBAN_COLUMNS,
        columns={"completed": jobs},
        filters={},
        color_options=[],
        status_options=[],
    )


def _find_job(job_id: int):
    return job_repo.get_job(job_id)


@bp.get("/<int:job_id>")
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


@bp.get("/<int:job_id>/photos.json")
def photos_json(job_id: int):
    photos = job_repo.list_photos(job_id)
    items = []
    for p in photos:
        fname = p.filename or ""
        ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
        kind = "pdf" if ext == "pdf" else "image"
        items.append(
            {
                "id": p.id,
                "filename": fname,
                "original_name": p.original_name,
                "url": url_for("uploads", name=fname),
                "kind": kind,
            }
        )
    return jsonify(items)


@bp.post("/<int:job_id>/photos/upload")
def upload_photo(job_id: int):
    file = request.files.get("file")
    if not file:
        return {"error": "file missing"}, 400
    # In parity mode we save filename only; storage handled by web server/volume
    job_repo.add_photo(job_id, filename=file.filename, original_name=file.filename)
    flash("Photo uploaded", "success")
    return redirect(url_for("jobs.detail", job_id=job_id))


@bp.post("/<int:job_id>/photos/<int:photo_id>/delete")
def delete_photo(job_id: int, photo_id: int):
    ok = job_repo.delete_photo(job_id, photo_id)
    flash("Photo deleted" if ok else "Photo not found", "success" if ok else "error")
    return redirect(url_for("jobs.detail", job_id=job_id))


@bp.post("/screen/reorder")
def screen_reorder():
    payload = request.get_json(silent=True) or {}
    job_ids = payload.get("job_ids") or []
    job_repo.reorder_screen([int(j) for j in job_ids])
    return jsonify({"ok": True})


@bp.post("/reorder")
def reorder_jobs():
    """Reorder jobs globally by provided id order (legacy parity)."""
    payload = request.get_json(silent=True) or {}
    order = payload.get("order") or []
    try:
        ids = [int(x) for x in order]
    except Exception:
        return jsonify({"error": "invalid order payload"}), 400
    job_repo.reorder_jobs(ids)
    return jsonify({"ok": True, "count": len(ids)})


@bp.post("/<int:job_id>/screen/add")
def screen_add(job_id: int):
    job_repo.set_on_screen(job_id, on_screen=True)
    return redirect(url_for("jobs.detail", job_id=job_id))


@bp.post("/<int:job_id>/screen/remove")
def screen_remove(job_id: int):
    job_repo.set_on_screen(job_id, on_screen=False)
    return redirect(url_for("jobs.detail", job_id=job_id))


@bp.get("/completed")
def completed():
    jobs = [j for j in job_repo.list_jobs() if (j.department or "").lower() == "completed"]
    return render_template("jobs/completed.html", jobs=jobs)


@bp.post("/<int:job_id>/archive")
def archive(job_id: int):
    job_repo.archive_job(job_id, reason=request.form.get("reason"))
    return redirect(url_for("jobs.detail", job_id=job_id))


@bp.post("/<int:job_id>/unarchive")
def unarchive(job_id: int):
    job_repo.unarchive_job(job_id)
    return redirect(url_for("jobs.detail", job_id=job_id))


@bp.post("/<int:job_id>/complete")
def complete(job_id: int):
    job_repo.complete_job(job_id)
    return redirect(url_for("jobs.detail", job_id=job_id))


@bp.post("/<int:job_id>/reopen")
def reopen(job_id: int):
    job_repo.reopen_job(job_id)
    return redirect(url_for("jobs.detail", job_id=job_id))


@bp.post("/<int:job_id>/delete")
def delete(job_id: int):
    job_repo.delete_job(job_id)
    flash("Job deleted", "success")
    return redirect(url_for("jobs.index"))


@bp.route("/<int:job_id>/edit", methods=["GET", "POST"])
def edit(job_id: int):
    """Render and process the job edit form."""
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

    form_data = _job_to_form_data(job)

    if request.method == "POST":
        contact_name = request.form.get("contact_name", "").strip() or None
        phone = request.form.get("phone", "").strip() or None
        email = request.form.get("email", "").strip() or None
        po = request.form.get("po", "").strip() or None
        job_type = request.form.get("type", "").strip() or None
        priority = request.form.get("priority", "").strip() or None
        blast = request.form.get("blast", "").strip() or None
        prep = request.form.get("prep", "").strip() or None
        color = request.form.get("color", "").strip() or None
        status = request.form.get("status", "").strip()
        department = request.form.get("department", "").strip()
        date_in_raw = request.form.get("date_in", "").strip()
        due_by_raw = request.form.get("due_by", "").strip()
        description = request.form.get("description", "").strip()
        notes = request.form.get("notes", "").strip()

        form_data.update(
            {
                "contact_name": contact_name or "",
                "phone": phone or "",
                "email": email or "",
                "po": po or "",
                "type": job_type or "",
                "priority": priority or "",
                "blast": blast or "",
                "prep": prep or "",
                "color": color or "",
                "status": status,
                "department": department,
                "date_in": date_in_raw,
                "due_by": due_by_raw,
                "description": description,
                "notes": notes,
            }
        )

        errors: list[str] = []
        status_options = list(dict.fromkeys(_STATUS_OPTIONS + ([job.status] if job.status else [])))

        if not status:
            errors.append("Status is required.")
        elif status not in status_options:
            errors.append("Select a valid status option.")

        department_keys = {value for value, _ in _DEPARTMENTS}
        if department and department not in department_keys:
            errors.append("Select a valid department.")

        if email and "@" not in email:
            errors.append("Enter a valid email address.")

        date_in = None
        if date_in_raw:
            try:
                date_in = date.fromisoformat(date_in_raw)
            except ValueError:
                errors.append("Date in must be a valid YYYY-MM-DD value.")

        due_by = None
        if due_by_raw:
            try:
                due_by = date.fromisoformat(due_by_raw)
            except ValueError:
                errors.append("Due date must be a valid YYYY-MM-DD value.")

        if errors:
            for error in errors:
                flash(error, "error")
            status_options = list(dict.fromkeys(_STATUS_OPTIONS + ([status] if status else [])))
            return render_template(
                "jobs/edit.html",
                job=job,
                form_options=_FORM_OPTIONS,
                departments=_DEPARTMENTS,
                status_options=status_options,
                form_data=form_data,
                is_admin=True,
            )

        job_repo.update_job(
            job_id,
            contact_name=contact_name,
            phone=phone,
            email=email,
            po=po,
            type=job_type,
            priority=priority,
            blast=blast,
            prep=prep,
            color=color,
            status=status,
            department=department or None,
            date_in=date_in,
            due_by=due_by,
            description=description,
            notes=notes,
        )
        flash("Job updated successfully", "success")
        return redirect(url_for("jobs.detail", job_id=job.id))

    status_options = list(dict.fromkeys(_STATUS_OPTIONS + ([job.status] if job.status else [])))
    return render_template(
        "jobs/edit.html",
        job=job,
        form_options=_FORM_OPTIONS,
        departments=_DEPARTMENTS,
        status_options=status_options,
        form_data=form_data,
        is_admin=True,
    )


@bp.get("/<int:job_id>/worksheet")
def worksheet(job_id: int):
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
    return render_template("jobs/worksheet.html", job=job)


@bp.post("/<int:job_id>/worksheet/save")
def worksheet_save(job_id: int):
    # For parity, persist shop_notes and customer_notes from form
    notes = request.form.get("shop_notes")
    customer_notes = request.form.get("customer_notes")
    job_repo.update_job(job_id, shop_notes=notes, customer_notes=customer_notes)
    flash("Worksheet saved", "success")
    return redirect(url_for("jobs.worksheet", job_id=job_id))
