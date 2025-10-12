from __future__ import annotations

import os

from flask import Blueprint, abort, redirect, render_template, send_from_directory, session, url_for

from ..core.branding import get_branding_settings
from ..core.config import UPLOADS_DIR
from ..core.db import get_ui_settings
from ..core.security import current_perms, is_admin, public_endpoint
from ..core.uploads import send_upload

bp = Blueprint("base", __name__)


@bp.route("/favicon.ico")
@public_endpoint
def favicon():
    try:
        branding = get_branding_settings()
        fav_rel = (branding.get("favicon") or "").strip() or None
        if fav_rel:
            uploads_dir = str(UPLOADS_DIR)
            candidate = os.path.join(uploads_dir, fav_rel)
            if os.path.commonpath([uploads_dir, os.path.abspath(candidate)]) == os.path.abspath(
                uploads_dir
            ) and os.path.exists(candidate):
                ext = candidate.rsplit(".", 1)[-1].lower() if "." in candidate else ""
                mime = {
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "svg": "image/svg+xml",
                    "ico": "image/x-icon",
                    "webp": "image/webp",
                }.get(ext, "image/png")
                rel_dir, rel_name = os.path.split(fav_rel)
                response = send_from_directory(
                    os.path.join(uploads_dir, rel_dir) if rel_dir else uploads_dir,
                    rel_name,
                    mimetype=mime,
                )
                try:
                    response.headers["Cache-Control"] = (
                        "no-store, no-cache, must-revalidate, max-age=0"
                    )
                    response.headers["Pragma"] = "no-cache"
                except Exception:
                    pass
                return response
        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
        candidates = [
            ("favicon-1.png", "image/png"),
            ("favicon.png", "image/png"),
            ("favicon.svg", "image/svg+xml"),
            ("favicon.ico", "image/vnd.microsoft.icon"),
        ]
        for rel, mime in candidates:
            path = os.path.join(static_dir, rel)
            if os.path.exists(path):
                response = send_from_directory(static_dir, rel, mimetype=mime)
                try:
                    response.headers["Cache-Control"] = (
                        "no-store, no-cache, must-revalidate, max-age=0"
                    )
                    response.headers["Pragma"] = "no-cache"
                except Exception:
                    pass
                return response
    except Exception:
        pass
    return abort(404)


@bp.route("/")
def home():
    return redirect(url_for("nav"))


@bp.route("/nav")
def nav():
    ui = get_ui_settings()
    return render_template(
        "nav.html",
        is_admin=is_admin(),
        show_csv=ui.get("show_csv", False),
        me_username=session.get("username"),
        perms=current_perms(),
    )


@bp.route("/uploads/<path:name>")
@public_endpoint
def uploaded_file(name):
    return send_upload(name)
