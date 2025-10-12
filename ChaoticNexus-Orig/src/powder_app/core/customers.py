from __future__ import annotations


def normalize_company(name: str) -> str:
    if not name:
        return ""
    return " ".join((name or "").strip().split())