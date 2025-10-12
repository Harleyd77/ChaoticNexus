from __future__ import annotations

import os
import secrets
import time
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from ..core.config import DEFAULT_FIRST_DEPT, UPLOADS_DIR
from ..core.customer_auth import (
    can_customer_access_intake,
    get_current_customer,
    get_customer_contact_info,
    is_customer_logged_in,
)
from ..core.customers import normalize_company
from ..core.db import connect, db_execute, db_query_one, is_postgres
from ..core.security import has_perm, is_admin
from ..core.uploads import allowed_upload

bp = Blueprint("intake", __name__)


@bp.route("/intake_form")
def intake_form():
    if not (is_admin() or has_perm("see_intake") or can_customer_access_intake()):
        return redirect(url_for("login", next=url_for("intake_form")))

    # Get customer information if logged in
    customer_info = get_customer_contact_info() if is_customer_logged_in() else {}

    return render_template(
        "intake_form.html",
        customer_info=customer_info,
        is_customer_logged_in=is_customer_logged_in(),
    )


@bp.route("/railing_intake")
def railing_intake():
    if not (is_admin() or has_perm("see_railing") or can_customer_access_intake()):
        return redirect(url_for("login", next=url_for("railing_intake")))

    # Get customer information if logged in
    customer_info = get_customer_contact_info() if is_customer_logged_in() else {}

    return render_template(
        "RailingIntake.html",
        customer_info=customer_info,
        is_customer_logged_in=is_customer_logged_in(),
    )


@bp.route("/submit", methods=["POST"])
def submit_form():
    if not (
        is_admin()
        or has_perm("see_intake")
        or has_perm("see_railing")
        or can_customer_access_intake()
    ):
        return redirect(url_for("login", next=url_for("intake_form")))

    form = request.form
    created = datetime.now().isoformat()

    # Get customer info if logged in
    customer = get_current_customer() if is_customer_logged_in() else None
    customer_account_id = customer["id"] if customer else None
    submitted_by_customer = customer is not None

    first_name = (form.get("first_name") or "").strip()
    last_name = (form.get("last_name") or "").strip()
    full_name = f"{first_name} {last_name}".strip()

    intake_source = (form.get("intake_source") or "production").strip().lower()
    if intake_source not in {"production", "railing"}:
        intake_source = "production"

    conn = connect()
    try:
        cursor = conn.cursor()
    except Exception:
        cursor = None

    if is_postgres():
        row = conn.execute(
            """
            INSERT INTO jobs
            (created_at, date_in, due_by, contact_name, company, phone, email, po, type, intake_source, priority, blast, prep, color, color_source, description, notes, status, department, customer_account_id, submitted_by_customer, requires_approval, archived, archived_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
            """,
            (
                created,
                form.get("dateIn"),
                form.get("dueBy"),
                full_name,
                form.get("company"),
                form.get("phone"),
                form.get("email"),
                form.get("po"),
                form.get("category") or "",
                intake_source,
                form.get("priority"),
                form.get("blast"),
                form.get("prep"),
                form.get("color"),
                form.get("color_source"),
                form.get("description"),
                form.get("notes"),
                "queued",
                DEFAULT_FIRST_DEPT,
                customer_account_id,
                bool(submitted_by_customer),
                bool(submitted_by_customer),  # requires_approval
                0,
                None,
            ),
        ).fetchone()
        job_id = row["id"] if row else None
    else:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO jobs
            (created_at, date_in, due_by, contact_name, company, phone, email, po, type, intake_source, priority, blast, prep, color, color_source, description, notes, status, department, customer_account_id, submitted_by_customer, requires_approval, archived, archived_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created,
                form.get("dateIn"),
                form.get("dueBy"),
                full_name,
                form.get("company"),
                form.get("phone"),
                form.get("email"),
                form.get("po"),
                form.get("category") or "",
                intake_source,
                form.get("priority"),
                form.get("blast"),
                form.get("prep"),
                form.get("color"),
                form.get("color_source"),
                form.get("description"),
                form.get("notes"),
                "queued",
                DEFAULT_FIRST_DEPT,
                customer_account_id,
                bool(submitted_by_customer),
                bool(submitted_by_customer),  # requires_approval
                0,  # archived
                None,
            ),
        )
        job_id = cursor.lastrowid

    files = request.files.getlist("photos") or []
    saved = 0
    for file in files:
        if not file or not getattr(file, "filename", None):
            continue
        if not allowed_upload(file.filename):
            continue
        original = file.filename or ""
        try:
            ext = "." + original.rsplit(".", 1)[-1].lower() if original else ""
            safe_base = (
                secure_filename(os.path.splitext(original)[0] if original else "") or "upload"
            )
        except (AttributeError, IndexError):
            ext = ""
            safe_base = "upload"
        unique = f"job{job_id}_{int(time.time())}_{secrets.token_hex(4)}"
        filename = safe_base[:40] + "_" + unique + ext
        path = os.path.join(UPLOADS_DIR, filename)
        try:
            file.save(path)
            if cursor is None:
                cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO job_photos (job_id, filename, original_name, created_at) VALUES (?,?,?,?)",
                (job_id, filename, original, created),
            )
            saved += 1
        except Exception:
            pass

    conn.commit()
    conn.close()

    try:
        if job_id:
            if saved > 0:
                flash(f"Job #{job_id} created. Uploaded {saved} file(s).", "success")
            else:
                flash(f"Job #{job_id} created.", "success")
    except Exception:
        pass

    company_normalized = normalize_company(form.get("company") or "")
    if company_normalized:
        row = db_query_one(
            "SELECT id FROM customers WHERE lower(trim(company)) = lower(trim(?))",
            (company_normalized,),
        )
        if row:
            db_execute(
                "UPDATE customers SET contact_name=?, phone=?, email=? WHERE id=?",
                (full_name, form.get("phone"), form.get("email"), row["id"]),
            )
        else:
            now = datetime.now().isoformat()
            try:
                db_execute(
                    """
                    INSERT INTO customers (company, contact_name, phone, email, address, notes, created_at)
                    VALUES (?, ?, ?, ?, '', '', ?)
                    """,
                    (company_normalized, full_name, form.get("phone"), form.get("email"), created),
                )
            except Exception:
                row2 = db_query_one(
                    "SELECT id FROM customers WHERE lower(trim(company)) = lower(trim(?))",
                    (company_normalized,),
                )
                if row2:
                    db_execute(
                        "UPDATE customers SET contact_name=?, phone=?, email=? WHERE id=?",
                        (full_name, form.get("phone"), form.get("email"), row2["id"]),
                    )

    # Redirect customers back to their portal, others back to the form
    if is_customer_logged_in():
        flash("Job submitted successfully! We'll review it and get back to you soon.", "success")
        return redirect(url_for("customer_portal.dashboard"))

    try:
        ref = request.referrer or ""
        if "/railing_intake" in ref:
            return redirect(url_for("railing_intake") + "?submitted=1")
    except Exception:
        pass
    return redirect(url_for("intake_form") + "?submitted=1")
