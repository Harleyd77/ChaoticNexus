from __future__ import annotations

import json

from .db import db_execute, db_query_one


def get_branding_settings() -> dict:
    row = db_query_one("SELECT value FROM settings WHERE name='branding'")
    data: dict = {}
    if row:
        try:
            data.update(json.loads(row["value"]))
        except Exception:
            pass
    return data


def save_branding_settings(payload: dict) -> None:
    exists = db_query_one("SELECT id FROM settings WHERE name='branding'")
    value = json.dumps(payload)
    if exists:
        db_execute("UPDATE settings SET value=? WHERE name='branding'", (value,))
    else:
        db_execute("INSERT INTO settings (name,value) VALUES (?,?)", ("branding", value))
