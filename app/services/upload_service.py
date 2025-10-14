"""Utilities for saving and deleting job-linked files.

Creates safe, unique filenames labeled with the job id and a timestamp.
Files are stored under UPLOADS_DIR/jobs/<company-seg>/job-<id>/, and the
function returns a relative path served by the /uploads/<name> route.
"""

from __future__ import annotations

import os
import re
import secrets
from collections.abc import Iterable
from datetime import datetime

from flask import current_app

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = _NON_ALNUM.sub("-", value).strip("-")
    return value or "job"


def build_job_upload_dir(job_id: int, company: str | None) -> str:
    """Return absolute directory for storing this job's files."""
    root = current_app.config.get("UPLOADS_DIR")
    seg = _slugify(company or "walk-ins")
    return os.path.join(root, "jobs", seg, f"job-{job_id}")


def allowed_extension(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in {"png", "jpg", "jpeg", "webp", "gif", "heic", "heif", "pdf"}


def save_job_files(job_id: int, company: str | None, files: Iterable) -> list[tuple[str, str]]:
    """Save uploaded files to disk with safe names.

    Returns list of (relative_path, original_name) for each successfully saved file.
    """
    saved: list[tuple[str, str]] = []
    upload_dir = build_job_upload_dir(job_id, company)
    try:
        os.makedirs(upload_dir, exist_ok=True)
    except Exception:
        # Fallback to root if nested path cannot be created
        upload_dir = current_app.config.get("UPLOADS_DIR")

    now = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    for f in files:
        if not f or not getattr(f, "filename", None):
            continue
        orig = f.filename or ""
        if not allowed_extension(orig):
            continue
        base, ext = os.path.splitext(orig)
        base = _slugify(base)[:40] or "upload"
        uniq = secrets.token_hex(4)
        filename = f"job{job_id}_{now}_{uniq}{ext.lower()}"
        # Preserve some context while ensuring uniqueness
        if base and base != "upload":
            filename = f"{base}_{filename}"
        abs_path = os.path.join(upload_dir, filename)
        try:
            f.save(abs_path)
            rel = os.path.relpath(abs_path, current_app.config.get("UPLOADS_DIR")).replace(
                "\\", "/"
            )
            saved.append((rel, orig))
        except Exception:
            continue
    return saved


def delete_uploaded_file(relative_path: str) -> bool:
    """Delete an uploaded file by its relative path under UPLOADS_DIR."""
    try:
        root = current_app.config.get("UPLOADS_DIR")
        abs_path = os.path.join(root, relative_path)
        # Safety: ensure path is within root
        if not os.path.abspath(abs_path).startswith(os.path.abspath(root)):
            return False
        if os.path.exists(abs_path):
            os.remove(abs_path)
            return True
    except Exception:
        return False
    return False
