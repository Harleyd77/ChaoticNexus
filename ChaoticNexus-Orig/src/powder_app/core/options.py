from __future__ import annotations

import json
import re

from .db import db_execute, db_query_one

_DEFAULT_POWDER_OPTIONS = {
    "color_families": [
        "Black",
        "White",
        "Grey",
        "Brown",
        "Green",
        "Blue",
        "Red",
        "Yellow",
        "Orange",
        "Metallic",
        "Other",
    ],
    "manufacturers": [
        "Prismatic Powders",
        "Tiger Drylac",
        "Cardinal",
        "Axalta",
        "Beyond Powder",
        "PPG",
    ],
    "gloss_levels": [
        "Gloss",
        "Semi-Gloss",
        "Satin",
        "Matte",
        "Flat",
    ],
    "finishes": [
        "Smooth",
        "Texture",
        "Wrinkle",
        "Sand",
        "Hammertone",
    ],
    "int_ext": [
        "Interior",
        "Exterior",
        "Interior / Exterior",
    ],
}

_DEFAULT_WORK_ORDER_OPTIONS = {
    "blast": ["No", "Light Etch", "Medium Etch", "Heavy Etch"],
    "tank": ["No", "Yes"],
    "pretreatment": ["None", "Degrease", "Wash", "Prime"],
    "quote": ["No", "Yes", "Pending"],
}


def _normalize_list(values: list[str] | None, default: list[str]) -> list[str]:
    if not isinstance(values, list):
        return default[:]
    seen = set()
    cleaned: list[str] = []
    for value in values:
        text = (value or "").strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
    return cleaned or default[:]


def get_powder_options() -> dict:
    row = db_query_one("SELECT value FROM settings WHERE name='powder_options'")
    payload = {}
    if row:
        try:
            payload.update(json.loads(row["value"]))
        except Exception:
            pass
    result = {key: _normalize_list(payload.get(key), default) for key, default in _DEFAULT_POWDER_OPTIONS.items()}
    # Add markup_percentage (not a list field)
    result["markup_percentage"] = payload.get("markup_percentage", 0)
    return result


def save_powder_options(payload: dict) -> None:
    exists = db_query_one("SELECT id FROM settings WHERE name='powder_options'")
    value = json.dumps(payload)
    if exists:
        db_execute("UPDATE settings SET value=? WHERE name='powder_options'", (value,))
    else:
        db_execute("INSERT INTO settings (name,value) VALUES (?,?)", ("powder_options", value))


def get_work_order_options() -> dict[str, list[str]]:
    row = db_query_one("SELECT value FROM settings WHERE name='work_order_options'")
    payload = {}
    if row:
        try:
            payload = json.loads(row["value"]) or {}
        except Exception:
            payload = {}
    return {key: _normalize_list(payload.get(key), default) for key, default in _DEFAULT_WORK_ORDER_OPTIONS.items()}


def save_work_order_options(payload: dict[str, list[str]]):
    exists = db_query_one("SELECT id FROM settings WHERE name='work_order_options'")
    value = json.dumps(payload)
    if exists:
        db_execute("UPDATE settings SET value=? WHERE name='work_order_options'", (value,))
    else:
        db_execute("INSERT INTO settings (name,value) VALUES (?,?)", ("work_order_options", value))


def get_intake_config_payload() -> dict:
    row = db_query_one("SELECT value FROM settings WHERE name='intake_config'")
    if row:
        try:
            return json.loads(row["value"]) or {}
        except Exception:
            return {}
    return {"options": {}, "required": {}}


def save_intake_config_payload(payload: dict) -> None:
    exists = db_query_one("SELECT id FROM settings WHERE name='intake_config'")
    value = json.dumps(payload)
    if exists:
        db_execute("UPDATE settings SET value=? WHERE name='intake_config'", (value,))
    else:
        db_execute("INSERT INTO settings (name,value) VALUES (?,?)", ("intake_config", value))


def get_railing_config_payload() -> dict:
    row = db_query_one("SELECT value FROM settings WHERE name='railing_intake_config'")
    if row:
        try:
            return json.loads(row["value"])
        except Exception:
            pass
    return {
        "options": {
            "prep": ["None Required", "Base /", "Full Prep", "Touch Up"],
            "blast": ["Light Etch", "Medium Etch", "Heavy Etch", "None"],
            "priority": ["Standard", "Rush", "Hot"],
            "section_type": ["Picket", "Glass", "Other"],
        },
        "required": {
            "dateIn": True,
            "dueBy": False,
            "name": True,
            "company": True,
            "phone": True,
            "email": True,
            "description": True,
            "prep": False,
            "blast": False,
            "priority": False,
            "color": True,
        },
    }


def save_railing_config_payload(payload: dict) -> None:
    exists = db_query_one("SELECT id FROM settings WHERE name='railing_intake_config'")
    value = json.dumps(payload)
    if exists:
        db_execute("UPDATE settings SET value=? WHERE name='railing_intake_config'", (value,))
    else:
        db_execute(
            "INSERT INTO settings (name, value) VALUES (?,?)",
            ("railing_intake_config", value),
        )
