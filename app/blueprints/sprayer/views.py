"""HTTP endpoints for the Sprayer blueprint."""

from flask import jsonify, redirect, render_template, request, url_for

from app.repositories import job_repo
from app.services.sprayer_service import sprayer_service

from . import bp


@bp.route("/hitlist")
def hitlist():
    """Sprayer hit list page (jobs on screen)."""
    jobs = [j for j in job_repo.list_jobs() if getattr(j, "on_screen", False)]
    return render_template(
        "sprayer/hitlist.html",
        jobs=jobs,
    )


@bp.route("/batches")
def batches():
    """Spray batches page."""
    powders, open_batches, recent = sprayer_service.dashboard()
    return render_template(
        "sprayer/batches.html",
        powders=powders,
        open_batches=open_batches,
        recent=recent,
    )


@bp.post("/batches/start")
def batches_start():
    powder_id = int(request.form.get("powder_id", 0))
    role = (request.form.get("role") or "primary").strip()
    operator = (request.form.get("operator") or "").strip()
    note = (request.form.get("note") or "").strip()
    start_weight_kg = float(request.form.get("start_weight_kg", "0") or "0")
    batch = sprayer_service.start_batch(
        powder_id=powder_id,
        role=role,
        operator=operator,
        note=note,
        start_weight_kg=start_weight_kg,
    )
    return redirect(url_for("sprayer.batch_detail", batch_id=batch.id))


@bp.get("/batches/<int:batch_id>")
def batch_detail(batch_id: int):
    batch, jobs = sprayer_service.batch_detail(batch_id)
    if not batch:
        return (render_template("errors/error.html", error="Batch Not Found", message=""), 404)
    candidates = [
        j
        for j in job_repo.list_jobs()
        if not any(getattr(row, "job_id", None) == j.id for row in jobs)
    ]
    return render_template(
        "sprayer/batch.html",
        batch=batch,
        jobs=jobs,
        candidates=candidates,
    )


@bp.get("/candidates.json")
def candidates_json():
    jobs = job_repo.list_jobs()
    return jsonify(
        [
            {"id": j.id, "company": j.company, "color": j.color, "due_by": j.due_by}
            for j in jobs
            if not getattr(j, "archived", False) and j.completed_at is None
        ]
    )


@bp.get("/hitlist.json")
def hitlist_json():
    jobs = job_repo.list_jobs()
    on_screen = [
        {
            "id": j.id,
            "company": j.company,
            "color": j.color,
            "due_by": j.due_by,
            "priority": j.priority,
        }
        for j in jobs
        if getattr(j, "on_screen", False)
    ]
    return jsonify(on_screen)


@bp.post("/batches/<int:batch_id>/add_job")
def batch_add_job(batch_id: int):
    job_ids: list[int] = []
    for val in request.form.getlist("job_id"):
        try:
            job_ids.append(int(val))
        except Exception:
            pass
    for jid in job_ids:
        sprayer_service.attach_job(batch_id, jid)
    return redirect(url_for("sprayer.batch_detail", batch_id=batch_id))


@bp.post("/batches/<int:batch_id>/job/<int:job_id>/start")
def job_start(batch_id: int, job_id: int):
    sprayer_service.start_job(batch_id, job_id)
    return jsonify(ok=True)


@bp.post("/batches/<int:batch_id>/job/<int:job_id>/end")
def job_end(batch_id: int, job_id: int):
    sprayer_service.end_job(batch_id, job_id)
    return jsonify(ok=True)


@bp.post("/batches/<int:batch_id>/close")
def batch_close(batch_id: int):
    end_weight_kg = float(request.form.get("end_weight_kg", "0") or "0")
    sprayer_service.close_batch(batch_id, end_weight_kg=end_weight_kg)
    return redirect(url_for("sprayer.batches"))


@bp.post("/batches/<int:batch_id>/job/<int:job_id>/remove")
def job_remove(batch_id: int, job_id: int):
    sprayer_service.remove_job(batch_id, job_id)
    return redirect(url_for("sprayer.batch_detail", batch_id=batch_id))
