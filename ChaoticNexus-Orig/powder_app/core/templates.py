from __future__ import annotations

import os
import urllib.parse
from pathlib import Path

from flask import request, url_for

from .branding import get_branding_settings
from .customer_auth import create_customer_context
from .security import is_admin
from .utils import clean_notes, slugify

TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"
STATIC_ROOT = Path(__file__).resolve().parents[1] / "static"


def ensure_template_encoding() -> None:
    for path in TEMPLATE_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".html", ".txt"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"Warning: Template file {path.name} is not UTF-8 encoded")
            continue
        if os.access(path, os.W_OK):
            path.write_text(content, encoding="utf-8", newline="\n")


def _asset(path: str) -> str:
    try:
        static_file = STATIC_ROOT / path
        if static_file.exists():
            version = int(static_file.stat().st_mtime)
            return url_for("static", filename=path, v=version)
        return url_for("static", filename=path)
    except Exception:
        return url_for("static", filename=path)


def _logo_path(name: str) -> str:
    try:
        key = (name or "").strip().lower()
        base = STATIC_ROOT / "logos"
        exts = (".png", ".webp", ".jpg", ".jpeg", ".svg", ".gif")
        candidates = [
            ("tiger drylac", ["tiger-drylac", "tiger_drylac", "tiger"]),
            ("prismatic powders", ["prismatic-powders", "prismatic"]),
            ("beyond powder", ["beyond powder", "beyond-powder", "beyond"]),
        ]
        for phrase, bases in candidates:
            if phrase in key:
                for bname in bases:
                    for ext in exts:
                        candidate = base / f"{bname}{ext}"
                        if candidate.exists():
                            return f"logos/{candidate.name}"
        try:
            files = list(base.iterdir())
        except Exception:
            files = []
        tokens = [item for item in key.replace("-", " ").split() if item]
        for file in files:
            if file.suffix not in exts:
                continue
            lower = file.name.lower()
            if any(token in lower for token in tokens):
                return f"logos/{file.name}"
        return ""
    except Exception:
        return ""


def _add_charset_header(response):
    if "text/html" in response.content_type or "application/json" in response.content_type:
        response.charset = "utf-8"
    return response


def _add_content_language(response):
    content_type = getattr(response, "content_type", "") or ""
    if "text/html" in content_type:
        response.headers.setdefault("Content-Language", "en")
    return response


def _update_qs(args, **kwargs):
    params = request.args.copy()
    for key, value in kwargs.items():
        params[key] = value
    return urllib.parse.urlencode(params)


def _create_branding_context():
    branding = get_branding_settings()
    favicon = branding.get("favicon")
    page_logo = branding.get("page_logo")

    # Handle both uploaded files (branding/...) and static files (static:logos/...)
    favicon_url = ""
    if favicon:
        if favicon.startswith("static:"):
            # Static file reference
            favicon_url = url_for("static", filename=favicon.replace("static:", ""))
        else:
            # Uploaded file
            favicon_url = url_for("uploaded_file", name=favicon)

    page_logo_url = ""
    if page_logo:
        if page_logo.startswith("static:"):
            # Static file reference
            page_logo_url = url_for("static", filename=page_logo.replace("static:", ""))
        else:
            # Uploaded file
            page_logo_url = url_for("uploaded_file", name=page_logo)

    return {
        "branding_favicon": favicon_url,
        "branding_page_logo": page_logo_url,
    }


def register_template_utils(app) -> None:
    app.context_processor(lambda: {"asset": _asset})
    app.context_processor(lambda: {"logo_path": _logo_path})
    app.context_processor(_create_branding_context)
    app.context_processor(create_customer_context)
    app.context_processor(lambda: {"is_admin": is_admin})
    app.template_filter("update_qs")(_update_qs)
    app.template_filter("slug")(slugify)
    app.template_filter("clean_notes")(clean_notes)
    app.after_request(_add_charset_header)
    app.after_request(_add_content_language)
