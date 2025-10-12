from __future__ import annotations

import csv
import json
import os
import secrets
import time
from datetime import datetime, timedelta
from io import StringIO

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from ..core.config import DEPARTMENTS, UPLOADS_DIR
from ..core.db import connect, db_execute, db_query_all, db_query_one, get_db, get_ui_settings
from ..core.errors import ValidationError
from ..core.options import get_work_order_options
from ..core.security import has_perm, is_admin, require_admin
from ..core.uploads import allowed_upload
from ..core.utils import fmt_ts, slugify

bp = Blueprint("jobs", __name__)

TIMER_ACTIVE_DEPARTMENTS = {"sandblaster", "prep", "sprayers"}


DATETIME_PARSE_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
)


PRIORITY_ORDER = {
    "emergency": 0,
    "rush": 1,
    "semi rush": 2,
}


def _parse_naive_dt(value):
    if not value:
        return None
    value = str(value).strip()
    if not value:
        return None
    probe = value[:19]
    for fmt in DATETIME_PARSE_FORMATS:
        try:
            return datetime.strptime(probe, fmt)
        except Exception:
            continue
    return None


def _priority_rank(priority):
    if not priority:
        return 99
    return PRIORITY_ORDER.get(priority.strip().lower(), 99)


def _department_label(dept):
    if not dept:
        return "Unassigned"
    slug = str(dept).strip()
    if not slug:
        return "Unassigned"
    return slug.replace("_", " ").title()


def _serialize_job_for_kanban(row, is_running, now, soon):
    status = (row.get("status") or "").strip()
    due_raw = row.get("due_by") or ""
    due_dt = _parse_naive_dt(due_raw)
    at_risk = False
    if due_dt and due_dt <= soon:
        if status.lower() not in {"completed", "complete", "done"}:
            at_risk = True
    priority = (row.get("priority") or "").strip()
    company = row.get("company") or ""
    card = {
        "id": row.get("id"),
        "company": company,
        "color": row.get("color") or "",
        "status": status,
        "status_slug": status.lower().replace(" ", "-") if status else "",
        "department": (row.get("department") or "").strip(),
        "description": row.get("description") or "",
        "priority": priority,
        "priority_rank": _priority_rank(priority),
        "due_pretty": due_dt.strftime("%b %d, %Y") if due_dt else (due_raw or ""),
        "due_raw": due_raw or "",
        "at_risk": at_risk,
        "is_running": bool(is_running),
        "_due_dt": due_dt,
    }
    return card


def validate_jobs_params(args):
    dept = (args.get("department") or "").strip().lower()
    if dept and dept not in DEPARTMENTS:
        raise ValidationError(f"Invalid department. Must be one of: {', '.join(DEPARTMENTS)}")

    comp = (args.get("company") or "").strip()
    if comp and len(comp) > 100:
        raise ValidationError("Company name is too long")

    search = (args.get("search") or "").strip()
    if search:
        if len(search) < 2:
            raise ValidationError("Search term must be at least 2 characters")
        if len(search) > 100:
            raise ValidationError("Search term is too long")
        if any(char in search for char in "%;\\"):
            raise ValidationError("Search contains invalid characters")

    valid_sorts = [
        "default",
        "created_desc",
        "created_asc",
        "due_asc",
        "due_desc",
        "company_az",
        "company_za",
        "priority_high",
        "on_screen_first",
    ]
    sort = (args.get("sort") or "default").strip()
    if sort not in valid_sorts:
        raise ValidationError(f"Invalid sort parameter. Must be one of: {', '.join(valid_sorts)}")

    try:
        page = max(1, int(args.get("page", 1)))
        per_page = min(100, max(10, int(args.get("per_page", 50))))
    except ValueError:
        raise ValidationError("Invalid pagination parameters")

    return {
        "department": dept,
        "company": comp,
        "search": search,
        "sort": sort,
        "show_archived": args.get("archived") == "1",
        "page": page,
        "per_page": per_page,
    }


@bp.route("/jobs")
def jobs_board():
    if not (is_admin() or has_perm("see_jobs")):
        return redirect(url_for("login", next=url_for("jobs.jobs_board")))
    try:
        clean = validate_jobs_params(request.args)
    except ValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("jobs.jobs_board"))

    dept = clean["department"]
    comp = clean["company"]
    search = clean["search"]
    sort = clean["sort"]
    show_archived = clean["show_archived"] and has_perm("see_archived")
    page = clean["page"]
    per_page = clean["per_page"]

    where_parts: list[str] = []
    params: list[str] = []
    if dept and dept in DEPARTMENTS:
        where_parts.append("department = ?")
        params.append(dept)
    if comp:
        where_parts.append("company = ?")
        params.append(comp)
    if search:
        search_like = f"%{search}%"
        where_parts.append(
            "(lower(company) LIKE lower(?) OR lower(contact_name) LIKE lower(?) "
            "OR lower(color) LIKE lower(?) OR lower(description) LIKE lower(?))"
        )
        params.extend([search_like, search_like, search_like, search_like])
    where_parts.append("COALESCE(archived,0) = 1" if show_archived else "COALESCE(archived,0) = 0")
    where_sql = "WHERE " + " AND ".join(where_parts) if where_parts else ""

    default_order = """
      ORDER BY
        CASE WHEN order_index IS NULL THEN 1 ELSE 0 END,
        order_index ASC,
        CASE priority
          WHEN 'Emergency' THEN 1
          WHEN 'Rush' THEN 2
          WHEN 'Semi Rush' THEN 3
          ELSE 4
        END,
        CASE WHEN due_by IS NULL OR due_by='' THEN 1 ELSE 0 END,
        due_by ASC,
        id DESC
    """
    order_clause = default_order
    if sort == "created_desc":
        order_clause = "ORDER BY created_at DESC, id DESC"
    elif sort == "created_asc":
        order_clause = "ORDER BY created_at ASC, id ASC"
    elif sort == "due_asc":
        order_clause = (
            "ORDER BY CASE WHEN due_by IS NULL OR due_by='' THEN 1 ELSE 0 END, due_by ASC, id DESC"
        )
    elif sort == "due_desc":
        order_clause = (
            "ORDER BY CASE WHEN due_by IS NULL OR due_by='' THEN 1 ELSE 0 END, due_by DESC, id DESC"
        )
    elif sort == "company_az":
        order_clause = "ORDER BY LOWER(company) ASC, id DESC"
    elif sort == "company_za":
        order_clause = "ORDER BY LOWER(company) DESC, id DESC"
    elif sort == "priority_high":
        order_clause = """
          ORDER BY
            CASE priority
              WHEN 'Emergency' THEN 1
              WHEN 'Rush' THEN 2
              WHEN 'Semi Rush' THEN 3
              ELSE 4
            END,
            id DESC
        """
    elif sort == "on_screen_first":
        order_clause = "ORDER BY CASE WHEN on_screen=1 THEN 0 ELSE 1 END, id DESC"

    count_sql = f"SELECT COUNT(*) as total FROM jobs {where_sql}"
    total_count = db_query_one(count_sql, tuple(params))["total"]
    total_pages = (total_count + per_page - 1) // per_page
    limit_sql = f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"

    rows = db_query_all(
        f"""SELECT id, created_at, date_in, due_by, contact_name, company,
                  phone, email, description, notes, status, department,
                  color, blast, prep, priority, on_screen, completed_at
           FROM jobs {where_sql} {order_clause} {limit_sql}""",
        tuple(params),
    )

    open_set = set()
    photos_count_map: dict[int, int] = {}
    if rows:
        job_ids = tuple(r["id"] for r in rows)
        placeholders = ",".join(["?"] * len(job_ids))
        open_rows = db_query_all(
            f"SELECT job_id, department FROM time_logs WHERE end_ts IS NULL AND job_id IN ({placeholders})",
            job_ids,
        )
        open_set = {(r["job_id"], r["department"]) for r in open_rows}
        pc_rows = db_query_all(
            f"SELECT job_id, COUNT(*) AS c FROM job_photos WHERE job_id IN ({placeholders}) GROUP BY job_id",
            job_ids,
        )
        photos_count_map = {r["job_id"]: r["c"] for r in pc_rows}

    decorated = []
    for r in rows:
        d = dict(r)
        d["created_pretty"] = fmt_ts(d.get("created_at") or "")
        d["is_running"] = (d["id"], d.get("department")) in open_set
        d["photos_count"] = int(photos_count_map.get(d["id"], 0))
        decorated.append(d)

    enable_virtual_scroll = False
    return render_template(
        "jobs.html",
        rows=decorated,
        departments=DEPARTMENTS,
        active_department=dept,
        show_archived=show_archived,
        is_admin=is_admin(),
        show_csv=get_ui_settings().get("show_csv", False),
        page_title="Job Database",
        screen_mode=False,
        reorder_endpoint=url_for("jobs.jobs_reorder"),
        enable_virtual_scroll=enable_virtual_scroll,
        storage_key="vpc_job_order",
        sort=sort,
        company=comp,
        request=request,
        photos_count_map=photos_count_map,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_count=total_count,
    )


@bp.route("/jobs/<int:job_id>/photos.json")
def job_photos_json(job_id: int):
    rows = db_query_all(
        "SELECT id, filename, original_name, created_at FROM job_photos WHERE job_id=? ORDER BY id DESC",
        (job_id,),
    )
    items = []
    for r in rows:
        fname = r["filename"] or ""
        ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
        kind = "pdf" if ext == "pdf" else "image"
        items.append(
            {
                "id": r["id"],
                "filename": fname,
                "original_name": r["original_name"],
                "url": url_for("base.uploaded_file", name=fname),
                "kind": kind,
            }
        )
    return jsonify(items)


@bp.route("/jobs/reorder", methods=["POST"])
def jobs_reorder():
    guard = require_admin()
    if guard:
        return guard
    payload = request.get_json(force=True, silent=False) or {}
    order = payload.get("order") or []
    try:
        ids = [int(x) for x in order]
    except Exception:
        abort(400, "Invalid order payload")
    idx = 1
    for job_id in ids:
        db_execute("UPDATE jobs SET order_index=? WHERE id=?", (idx, job_id))
        idx += 1
    return jsonify({"ok": True, "count": len(ids)})


@bp.route("/jobs/kanban")
def jobs_kanban():
    if not (is_admin() or has_perm("see_jobs")):
        return redirect(url_for("login", next=url_for("jobs.jobs_kanban")))

    search = (request.args.get("search") or "").strip()
    color_filter = (request.args.get("color") or "").strip()
    status_filter = (request.args.get("status") or "").strip()

    where_parts = ["COALESCE(archived,0)=0"]
    params: list[str] = []
    if search:
        like = f"%{search}%"
        where_parts.append(
            "(lower(company) LIKE lower(?) OR lower(contact_name) LIKE lower(?) "
            "OR lower(color) LIKE lower(?) OR lower(description) LIKE lower(?))"
        )
        params.extend([like, like, like, like])
    if color_filter:
        where_parts.append("lower(color) = lower(?)")
        params.append(color_filter)
    if status_filter:
        where_parts.append("lower(status) = lower(?)")
        params.append(status_filter)

    where_sql = "WHERE " + " AND ".join(where_parts) if where_parts else ""
    order_clause = """
        ORDER BY
            CASE priority
              WHEN 'Emergency' THEN 1
              WHEN 'Rush' THEN 2
              WHEN 'Semi Rush' THEN 3
              ELSE 4
            END,
            CASE WHEN due_by IS NULL OR due_by='' THEN 1 ELSE 0 END,
            due_by ASC,
            id DESC
    """

    rows = db_query_all(
        f"""SELECT id, company, color, status, department, due_by, priority, description
               FROM jobs {where_sql} {order_clause}""",
        tuple(params),
    )

    job_ids = [row["id"] for row in rows]
    running_jobs: set[int] = set()
    if job_ids:
        placeholders = ",".join(["?"] * len(job_ids))
        running_rows = db_query_all(
            f"SELECT job_id FROM time_logs WHERE end_ts IS NULL AND job_id IN ({placeholders})",
            tuple(job_ids),
        )
        running_jobs = {r["job_id"] for r in running_rows}

    columns: dict[str, list[dict]] = {dept: [] for dept in DEPARTMENTS}
    column_order: list[str] = list(DEPARTMENTS)
    now = datetime.utcnow()
    soon = now + timedelta(hours=24)

    for row in rows:
        row_dict = dict(row)
        dept_value = (row_dict.get("department") or "").strip().lower()
        key = dept_value if dept_value in columns else "unassigned"
        if key not in columns:
            columns[key] = []
        if key not in column_order:
            column_order.append(key)
        card = _serialize_job_for_kanban(row_dict, row_dict["id"] in running_jobs, now, soon)
        card["department"] = key
        card["department_label"] = _department_label(key)
        columns[key].append(card)

    far_future = now + timedelta(days=3650)
    for key, items in columns.items():
        items.sort(
            key=lambda job: (
                job.get("priority_rank", 99),
                job.get("_due_dt") or far_future,
                -(job.get("id") or 0),
            )
        )
        for job in items:
            job.pop("_due_dt", None)

    color_rows = db_query_all(
        "SELECT DISTINCT color FROM jobs WHERE color IS NOT NULL AND TRIM(color)<>'' AND COALESCE(archived,0)=0 ORDER BY color"
    )
    color_options = [row["color"] for row in color_rows]
    if color_filter and color_filter not in color_options:
        color_options.append(color_filter)
    color_options = sorted(color_options, key=lambda c: c.lower())

    status_rows = db_query_all(
        "SELECT DISTINCT status FROM jobs WHERE status IS NOT NULL AND TRIM(status)<>'' ORDER BY status"
    )
    status_options = [row["status"] for row in status_rows]
    if status_filter and status_filter not in status_options:
        status_options.append(status_filter)
    status_options = sorted({s for s in status_options if s}, key=lambda s: s.lower())

    columns_meta = [
        {
            "key": key,
            "label": _department_label(key),
            "timer": key in TIMER_ACTIVE_DEPARTMENTS,
        }
        for key in column_order
        if key in columns
    ]

    return render_template(
        "jobs_kanban.html",
        columns=columns,
        columns_meta=columns_meta,
        filters={
            "search": search,
            "color": color_filter,
            "status": status_filter,
        },
        color_options=color_options,
        status_options=status_options,
        timer_departments=TIMER_ACTIVE_DEPARTMENTS,
        is_admin=is_admin(),
    )


@bp.post("/api/jobs/kanban/move")
def jobs_kanban_move():
    if not (is_admin() or has_perm("see_jobs")):
        return jsonify({"ok": False, "error": "Authentication required"}), 401

    payload = request.get_json(silent=True) or {}
    job_id = payload.get("job_id")
    target_dept = (payload.get("department") or "").strip().lower()

    try:
        job_id = int(job_id)
    except (TypeError, ValueError):
        abort(400, "Invalid job id")

    if target_dept not in DEPARTMENTS:
        abort(400, "Invalid department")

    job_row = db_query_one(
        "SELECT id, department, company, color, status, due_by, priority, description FROM jobs WHERE id=?",
        (job_id,),
    )
    if not job_row:
        abort(404)

    current_dept = (job_row["department"] or "").strip().lower()
    now = datetime.utcnow()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    if current_dept == target_dept:
        job_dict = dict(job_row)
        job_dict["department"] = target_dept
        card = _serialize_job_for_kanban(
            job_dict, target_dept in TIMER_ACTIVE_DEPARTMENTS, now, now + timedelta(hours=24)
        )
        card["department"] = target_dept
        card["department_label"] = _department_label(target_dept)
        card.pop("_due_dt", None)
        return jsonify({"ok": True, "job": card, "unchanged": True})

    db = get_db()
    db.execute("UPDATE jobs SET department=? WHERE id=?", (target_dept, job_id))
    db.execute(
        "UPDATE time_logs SET end_ts=?, minutes = ROUND(EXTRACT(EPOCH FROM (?::timestamp - start_ts::timestamp))/60, 1) WHERE job_id=? AND end_ts IS NULL",
        (now_str, now_str, job_id),
    )

    is_running = False
    if target_dept in TIMER_ACTIVE_DEPARTMENTS:
        db.execute(
            "INSERT INTO time_logs (job_id, department, start_ts) VALUES (?,?,?)",
            (job_id, target_dept, now_str),
        )
        is_running = True

    db.commit()

    updated_row = db_query_one(
        "SELECT id, department, company, color, status, due_by, priority, description FROM jobs WHERE id=?",
        (job_id,),
    )
    job_dict = dict(updated_row)
    job_dict["department"] = target_dept
    card = _serialize_job_for_kanban(job_dict, is_running, now, now + timedelta(hours=24))
    card["department"] = target_dept
    card["department_label"] = _department_label(target_dept)
    card.pop("_due_dt", None)
    return jsonify({"ok": True, "job": card})


@bp.route("/jobs/screen")
def jobs_screen():
    if not has_perm("see_job_screen"):
        return redirect(url_for("nav"))
    order_clause = """
      ORDER BY
        CASE WHEN screen_order_index IS NULL THEN 1 ELSE 0 END,
        screen_order_index ASC,
        CASE priority
          WHEN 'Emergency' THEN 1
          WHEN 'Rush' THEN 2
          WHEN 'Semi Rush' THEN 3
          ELSE 4
        END,
        CASE WHEN due_by IS NULL OR due_by='' THEN 1 ELSE 0 END,
        due_by ASC,
        id DESC
    """
    rows = db_query_all(
        f"SELECT * FROM jobs WHERE COALESCE(archived,0)=0 AND on_screen=1 AND (completed_at IS NULL OR TRIM(completed_at)='') {order_clause}"
    )
    open_set = set()
    photos_count_map = {}
    if rows:
        job_ids = tuple(r["id"] for r in rows)
        placeholders = ",".join(["?"] * len(job_ids))
        open_rows = db_query_all(
            f"SELECT job_id, department FROM time_logs WHERE end_ts IS NULL AND job_id IN ({placeholders})",
            job_ids,
        )
        open_set = {(r["job_id"], r["department"]) for r in open_rows}
        pc_rows = db_query_all(
            f"SELECT job_id, COUNT(*) AS c FROM job_photos WHERE job_id IN ({placeholders}) GROUP BY job_id",
            job_ids,
        )
        photos_count_map = {r["job_id"]: r["c"] for r in pc_rows}
    decorated = []
    for r in rows:
        d = dict(r)
        d["created_pretty"] = fmt_ts(d.get("created_at") or "")
        d["completed_pretty"] = fmt_ts(d.get("completed_at") or "")
        d["is_running"] = (d["id"], d.get("department")) in open_set
        d["photos_count"] = int(photos_count_map.get(d["id"], 0))
        decorated.append(d)
    return render_template(
        "jobs.html",
        rows=decorated,
        departments=DEPARTMENTS,
        active_department="",
        show_archived=False,
        is_admin=is_admin(),
        show_csv=False,
        page_title="Daily Hit List",
        screen_mode=True,
        reorder_endpoint=url_for("jobs.jobs_screen_reorder"),
        enable_virtual_scroll=False,
        storage_key="vpc_job_screen_order",
    )


@bp.route("/jobs/completed")
def jobs_completed():
    if not (is_admin() or has_perm("see_jobs")):
        return redirect(url_for("login", next=url_for("jobs.jobs_completed")))
    rows = db_query_all(
        """
        SELECT * FROM jobs
         WHERE COALESCE(archived,0)=0 AND completed_at IS NOT NULL AND TRIM(completed_at) <> ''
         ORDER BY id DESC
        """
    )
    open_set = set()
    photos_count_map = {}
    if rows:
        job_ids = tuple(r["id"] for r in rows)
        placeholders = ",".join(["?"] * len(job_ids))
        open_rows = db_query_all(
            f"SELECT job_id, department FROM time_logs WHERE end_ts IS NULL AND job_id IN ({placeholders})",
            job_ids,
        )
        open_set = {(r["job_id"], r["department"]) for r in open_rows}
        pc_rows = db_query_all(
            f"SELECT job_id, COUNT(*) AS c FROM job_photos WHERE job_id IN ({placeholders}) GROUP BY job_id",
            job_ids,
        )
        photos_count_map = {r["job_id"]: r["c"] for r in pc_rows}
    decorated = []
    for r in rows:
        d = dict(r)
        d["created_pretty"] = fmt_ts(d.get("created_at") or "")
        d["completed_pretty"] = fmt_ts(d.get("completed_at") or "")
        d["is_running"] = (d["id"], d.get("department")) in open_set
        d["photos_count"] = int(photos_count_map.get(d["id"], 0))
        decorated.append(d)
    return render_template(
        "jobs.html",
        rows=decorated,
        departments=DEPARTMENTS,
        active_department="",
        show_archived=False,
        is_admin=is_admin(),
        show_csv=False,
        page_title="Completed Jobs",
        screen_mode=False,
        reorder_endpoint=url_for("jobs.jobs_reorder"),
        enable_virtual_scroll=False,
        storage_key="vpc_job_order",
        completed_view=True,
    )


@bp.route("/jobs/<int:job_id>/screen/add", methods=["POST"])
def jobs_screen_add(job_id: int):
    guard = require_admin()
    if guard:
        return guard
    db_execute("UPDATE jobs SET on_screen=1 WHERE id=?", (job_id,))
    return redirect(request.referrer or url_for("jobs.jobs_board"))


@bp.route("/jobs/<int:job_id>/screen/remove", methods=["POST"])
def jobs_screen_remove(job_id: int):
    guard = require_admin()
    if guard:
        return guard
    db_execute("UPDATE jobs SET on_screen=0 WHERE id=?", (job_id,))
    return redirect(request.referrer or url_for("jobs.jobs_screen"))


@bp.route("/jobs/screen/reorder", methods=["POST"])
def jobs_screen_reorder():
    guard = require_admin()
    if guard:
        return guard
    payload = request.get_json(force=True, silent=False) or {}
    order = payload.get("order") or []
    try:
        ids = [int(x) for x in order]
    except Exception:
        abort(400, "Invalid order payload")
    idx = 1
    for job_id in ids:
        db_execute("UPDATE jobs SET screen_order_index=? WHERE id=?", (idx, job_id))
        idx += 1
    return jsonify({"ok": True, "count": len(ids)})


@bp.route("/jobs.csv")
def jobs_csv():
    ui = get_ui_settings()
    if not ui.get("show_csv", False):
        abort(404)
    if not (is_admin() or has_perm("see_csv")):
        return redirect(url_for("login", next=request.path))

    include_archived = request.args.get("include_archived") == "1"
    dept = (request.args.get("department") or "").strip().lower()

    where_parts, params = [], []
    if dept and dept in DEPARTMENTS:
        where_parts.append("department = ?")
        params.append(dept)
    if not include_archived:
        where_parts.append("COALESCE(archived,0) = 0")
    where_sql = "WHERE " + " AND ".join(where_parts) if where_parts else ""

    rows = db_query_all(
        f"""
        SELECT id, created_at, date_in, due_by, contact_name, company, phone, email, po,
               type, priority, prep, color, description, notes, department, archived, archived_reason, completed_at
          FROM jobs
          {where_sql}
          ORDER BY id DESC
        """,
        tuple(params),
    )

    fieldnames = [
        "id",
        "created_at",
        "date_in",
        "due_by",
        "contact_name",
        "company",
        "phone",
        "email",
        "po",
        "type",
        "priority",
        "prep",
        "color",
        "description",
        "notes",
        "department",
        "archived",
        "archived_reason",
        "completed_at",
    ]
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        record = {k: row[k] for k in fieldnames}
        if record["created_at"]:
            record["created_at"] = fmt_ts(record["created_at"])
        writer.writerow(record)
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": 'attachment; filename="jobs.csv"'},
    )


@bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id: int):
    if not is_admin():
        return redirect(url_for("login", next=request.path))
    job = db_query_one("SELECT * FROM jobs WHERE id=?", (job_id,))
    if not job:
        abort(404)
    if request.method == "POST":
        f = request.form
        db_execute(
            """
            UPDATE jobs
               SET date_in=?, due_by=?, contact_name=?, company=?, phone=?, email=?, po=?,
                   type=?, priority=?, blast=?, prep=?, color=?, description=?, notes=?, department=?, status=?
             WHERE id=?
            """,
            (
                f.get("date_in"),
                f.get("due_by"),
                f.get("contact_name"),
                f.get("company"),
                f.get("phone"),
                f.get("email"),
                f.get("po"),
                f.get("type"),
                f.get("priority"),
                f.get("blast"),
                f.get("prep"),
                f.get("color"),
                f.get("description"),
                f.get("notes"),
                f.get("department"),
                f.get("status"),
                job_id,
            ),
        )
        return redirect(url_for("jobs.jobs_board"))

    cfg_row = db_query_one("SELECT value FROM settings WHERE name='intake_config'")
    cfg = json.loads(cfg_row["value"]) if cfg_row else {"options": {}, "required": {}}
    photos = db_query_all("SELECT * FROM job_photos WHERE job_id=? ORDER BY id DESC", (job_id,))
    return render_template(
        "job_edit.html",
        job=job,
        departments=DEPARTMENTS,
        cfg=cfg,
        is_admin=is_admin(),
        photos=photos,
    )


def _job_asset_dir(job_id: int) -> str:
    try:
        row = db_query_one("SELECT company FROM jobs WHERE id=?", (job_id,))
        company = (row and (row.get("company") if isinstance(row, dict) else row["company"])) or ""
    except Exception:
        company = ""
    seg = slugify(company) or "walk-ins"
    return os.path.join(UPLOADS_DIR, "jobs", seg, f"job-{job_id}")


@bp.route("/jobs/<int:job_id>/photos/upload", methods=["POST"])
def job_photos_upload(job_id: int):
    guard = require_admin()
    if guard:
        return guard
    job = db_query_one("SELECT id FROM jobs WHERE id=?", (job_id,))
    if not job:
        abort(404)

    conn = connect()
    cursor = conn.cursor()
    created = datetime.now().isoformat()
    files = request.files.getlist("photos") or []
    saved = 0

    target_dir = _job_asset_dir(job_id)
    try:
        os.makedirs(target_dir, exist_ok=True)
    except Exception:
        target_dir = UPLOADS_DIR

    for file in files:
        if not file or not getattr(file, "filename", None):
            continue
        if not allowed_upload(file.filename):
            continue
        orig = file.filename or ""
        try:
            ext = "." + orig.rsplit(".", 1)[-1].lower() if orig else ""
            safe_base = secure_filename(os.path.splitext(orig)[0] if orig else "") or "upload"
        except (AttributeError, IndexError):
            ext = ""
            safe_base = "upload"
        unique = f"job{job_id}_{int(time.time())}_{secrets.token_hex(4)}"
        filename = safe_base[:40] + "_" + unique + ext
        path = os.path.join(target_dir, filename)
        try:
            file.save(path)
            rel = os.path.relpath(path, UPLOADS_DIR).replace("\\", "/")
            cursor.execute(
                "INSERT INTO job_photos (job_id, filename, original_name, created_at) VALUES (?,?,?,?)",
                (job_id, rel, orig, created),
            )
            saved += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    return redirect(url_for("jobs.edit_job", job_id=job_id))


@bp.route("/jobs/<int:job_id>/photos/<int:photo_id>/delete", methods=["POST"])
def job_photo_delete(job_id: int, photo_id: int):
    guard = require_admin()
    if guard:
        return guard
    row = db_query_one(
        "SELECT filename FROM job_photos WHERE id=? AND job_id=?", (photo_id, job_id)
    )
    if row:
        fname = row["filename"]
        try:
            os.remove(os.path.join(UPLOADS_DIR, fname))
        except Exception:
            pass
        db_execute("DELETE FROM job_photos WHERE id=?", (photo_id,))
    return redirect(url_for("jobs.edit_job", job_id=job_id))


@bp.route("/jobs/<int:job_id>/archive", methods=["POST"])
def archive_job(job_id: int):
    if not is_admin():
        return redirect(url_for("login", next=url_for("jobs.jobs_board")))
    reason = (request.form.get("reason") or "").strip()
    db_execute(
        "UPDATE jobs SET archived=1, archived_reason=?, on_screen=0 WHERE id=?", (reason, job_id)
    )
    return redirect(request.referrer or url_for("jobs.jobs_board"))


@bp.route("/jobs/<int:job_id>/unarchive", methods=["POST"])
def unarchive_job(job_id: int):
    if not is_admin():
        return redirect(url_for("login", next=url_for("jobs.jobs_board")))
    db_execute("UPDATE jobs SET archived=0, archived_reason=NULL WHERE id=?", (job_id,))
    return redirect(request.referrer or url_for("jobs.jobs_board"))


@bp.route("/jobs/<int:job_id>/complete", methods=["POST"])
def jobs_complete(job_id: int):
    if not is_admin():
        return redirect(url_for("login", next=url_for("jobs.jobs_board")))
    db_execute(
        "UPDATE jobs SET on_screen=0, completed_at=? WHERE id=?",
        (datetime.now().isoformat(), job_id),
    )
    return redirect(request.referrer or url_for("jobs.jobs_board"))


@bp.route("/jobs/<int:job_id>/reopen", methods=["POST"])
def jobs_reopen(job_id: int):
    if not is_admin():
        return redirect(url_for("login", next=url_for("jobs.jobs_board")))
    db_execute("UPDATE jobs SET completed_at=NULL WHERE id=?", (job_id,))
    return redirect(request.referrer or url_for("jobs.jobs_board"))


@bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
def jobs_delete(job_id: int):
    guard = require_admin()
    if guard:
        return guard
    try:
        rows = db_query_all("SELECT filename FROM job_photos WHERE job_id=?", (job_id,))
    except Exception:
        rows = []
    for r in rows or []:
        fname = r.get("filename") if isinstance(r, dict) else r["filename"]
        if not fname:
            continue
        try:
            os.remove(os.path.join(UPLOADS_DIR, fname))
        except Exception:
            pass
    try:
        db_execute("DELETE FROM job_photos WHERE job_id=?", (job_id,))
        db_execute("DELETE FROM time_logs WHERE job_id=?", (job_id,))
        db_execute("DELETE FROM job_powders WHERE job_id=?", (job_id,))
        db_execute("DELETE FROM spray_batch_jobs WHERE job_id=?", (job_id,))
        db_execute("DELETE FROM powder_usage WHERE job_id=?", (job_id,))
    except Exception:
        pass
    db_execute("DELETE FROM jobs WHERE id=?", (job_id,))
    flash("Job deleted.", "success")
    return redirect(url_for("jobs.jobs_board"))


@bp.route("/jobs/<int:job_id>")
def job_detail(job_id: int):
    job = db_query_one("SELECT * FROM jobs WHERE id=?", (job_id,))
    if not job:
        abort(404)
    photos = db_query_all(
        "SELECT id, filename, original_name, created_at FROM job_photos WHERE job_id=? ORDER BY id DESC",
        (job_id,),
    )
    return render_template(
        "job_view.html",
        job=job,
        photos=photos,
        is_admin=is_admin(),
    )


@bp.route("/jobs/<int:job_id>/worksheet")
def job_workorder(job_id: int):
    if not (is_admin() or has_perm("see_jobs")):
        return redirect(url_for("login", next=request.path))
    job = db_query_one("SELECT * FROM jobs WHERE id=?", (job_id,))
    if not job:
        abort(404)
    photos = db_query_all("SELECT id FROM job_photos WHERE job_id=?", (job_id,))
    meta_raw = job.get("work_order_json") if isinstance(job, dict) else job["work_order_json"]
    if isinstance(meta_raw, bytes):
        meta_raw = meta_raw.decode("utf-8", "ignore")
    if isinstance(meta_raw, str):
        try:
            worksheet_meta = json.loads(meta_raw) or {}
        except Exception:
            worksheet_meta = {}
    elif isinstance(meta_raw, dict):
        worksheet_meta = dict(meta_raw)
    else:
        worksheet_meta = {}

    raw_date = next(
        (
            job.get(key) if isinstance(job, dict) else job[key]
            for key in ("date_in", "due_by", "created_at")
            if (job.get(key) if isinstance(job, dict) else job[key])
        ),
        None,
    )
    display_date = None
    if raw_date:
        parsed = None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(raw_date[:19], fmt)
                break
            except Exception:
                parsed = None
        display_date = parsed.strftime("%d %b %y") if parsed else raw_date

    def _row_get(row, key):
        try:
            return row[key]
        except Exception:
            try:
                return row.get(key)
            except Exception:
                return None

    source = (_row_get(job, "intake_source") or "").strip().lower()
    if not source:
        job_type = (_row_get(job, "type") or "").strip().lower()
        if job_type == "railing":
            source = "railing"
        elif job_type:
            source = "production"

    template_type = "job_worksheet_railing" if source == "railing" else "job_worksheet_production"
    template_label = (
        "Railing Intake Worksheet"
        if template_type == "job_worksheet_railing"
        else "Production Intake Worksheet"
    )

    job_defaults = {
        "customer": (_row_get(job, "company") or ""),
        "blast": (_row_get(job, "blast") or ""),
        "tank": "No",
        "pretreatment": (_row_get(job, "prep") or ""),
        "colour": (_row_get(job, "color") or ""),
        "quote": "No",
        "po": (_row_get(job, "po") or ""),
        "promises_by": (_row_get(job, "due_by") or ""),
        "parts": (_row_get(job, "description") or ""),
        "fa_time": "",
        "measured_by": "",
        "powder_used": "",
        "total_blast_time": "",
        "total_spraying_time": "",
        "notes": (_row_get(job, "notes") or ""),
        "date": display_date or (raw_date or ""),
    }

    options = get_work_order_options()
    return render_template(
        "job_workorder.html",
        job=job,
        is_admin=is_admin(),
        photos_count=len(photos),
        has_photos=bool(photos),
        work_options=options,
        worksheet_meta=worksheet_meta,
        worksheet_date=display_date,
        worksheet_date_raw=raw_date,
        job_defaults=job_defaults,
        job_intake_source=source or "production",
        template_type=template_type,
        template_label=template_label,
    )


@bp.route("/jobs/<int:job_id>/worksheet/save", methods=["POST"])
def job_workorder_save(job_id: int):
    if not (is_admin() or has_perm("see_jobs")):
        return jsonify({"error": "forbidden"}), 403
    job = db_query_one("SELECT id FROM jobs WHERE id=?", (job_id,))
    if not job:
        abort(404)
    payload = request.get_json(force=True, silent=True) or {}
    if not isinstance(payload, dict):
        abort(400, "Invalid payload")
    allowed_keys = [
        "customer",
        "blast",
        "tank",
        "pretreatment",
        "colour",
        "quote",
        "po",
        "promises_by",
        "parts",
        "fa_time",
        "measured_by",
        "powder_used",
        "total_blast_time",
        "total_spraying_time",
        "notes",
        "date",
    ]
    meta: dict[str, str] = {}
    for key in allowed_keys:
        val = payload.get(key)
        if val is None:
            continue
        if isinstance(val, (str, int, float)):
            meta[key] = str(val).strip()
    db_execute("UPDATE jobs SET work_order_json=? WHERE id=?", (json.dumps(meta), job_id))
    return jsonify({"ok": True, "saved": len(meta)})
