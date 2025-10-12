from __future__ import annotations

from flask import send_from_directory

from .config import ALLOWED_UPLOAD_EXTENSIONS, UPLOADS_DIR


def allowed_upload(filename: str | None) -> bool:
    if not filename or "." not in filename:
        return False
    try:
        extension = filename.rsplit(".", 1)[-1].lower()
        return extension in ALLOWED_UPLOAD_EXTENSIONS
    except AttributeError:
        return False


def send_upload(name: str):
    return send_from_directory(UPLOADS_DIR, name)
