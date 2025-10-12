from __future__ import annotations

import re
from datetime import datetime


def fmt_ts(iso_str: str) -> str:
    try:
        return datetime.fromisoformat(iso_str).strftime("%b %d, %Y  %I:%M %p")
    except Exception:
        return iso_str or ""


def to_float(value):
    try:
        return float(value) if value not in (None, "") else None
    except Exception:
        return None


def slugify(value: str) -> str:
    try:
        text = (value or "").strip().lower()
        result: list[str] = []
        last_dash = False
        for char in text:
            if char.isalnum():
                result.append(char)
                last_dash = False
            elif not last_dash:
                result.append("-")
                last_dash = True
        return "".join(result).strip("-")
    except Exception:
        return ""


def clean_notes(value: str) -> str:
    try:
        text = value or ""
        phrases = [
            "Unmarked items won't be painted (ack)",
            "Engraving confirmed",
            "Storage policy acknowledged",
        ]
        for phrase in phrases:
            pattern = re.compile(
                r'(?:\s*\|\s*)?\s*[-"\u2013\u2014]?\s*' + re.escape(phrase) + r'(?:\s*\|\s*)?',
                re.IGNORECASE,
            )
            text = pattern.sub(" ", text)
        text = re.sub(r'\s*\|\s*', ' | ', text)
        text = re.sub(r'\s{2,}', ' ', text).strip(' |-\t\r\n')
        return text
    except Exception:
        return value or ""