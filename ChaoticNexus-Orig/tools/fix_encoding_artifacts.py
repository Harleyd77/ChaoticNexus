#!/usr/bin/env python3
"""
Quick cleanup for mojibake/encoding artifacts in HTML templates and inline strings.

This script performs conservative, targeted replacements to remove the most
visible artifacts observed after a bad encoding round-trip, without altering
logic. It also strips broken glyphs inside <span class="icon">...</span> blocks.

Run from repo root:
  python scripts/fix_encoding_artifacts.py
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "src" / "powder_app" / "templates",
    ROOT / "src" / "powder_app" / "main.py",  # inline admin panel HTML string
]


def clean_text(text: str) -> str:
    # Remove Unicode replacement char
    text = text.replace("\uFFFD", "")

    # Common mojibake fragments -> ascii/entities
    replacements = {
        "�?�": "&bull;",         # replacement char combos -> bullet
        "�?\"": "&mdash;",        # odd quote-like trio -> em dash
        "�+?": "",               # stray arrow chunk -> drop
        "�o.": ".",               # stray dot
        # Common UTF-8 mojibake sequences
        "Â·": "&middot;",         # middle dot (mojibake)
        "·": "&middot;",          # literal middle dot
        "â€”": "&mdash;",         # em dash
        "â€“": "&ndash;",         # en dash
        "â€¢": "&bull;",          # bullet (mojibake)
        "•": "&bull;",           # literal bullet
        "â€‹": "",                # zero-width space
        "â€˜": "'",               # left single quote
        "â€™": "'",               # right single quote
        "â€œ": '"',               # left double quote
        "â€�": '"',               # right double quote
        "Ã—": "x",                # multiplication sign
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # Normalize job title joiner in jobs.html if present
    text = re.sub(r"(#\{\{\s*r\.id\s*\}\})\s+[-–—Â·]*\s*", r"\\1 &mdash; ", text)

    # Strip broken icon glyphs while keeping the span for layout
    text = re.sub(r"(<span\s+class=\"icon\">)(.*?)(</span>)", r"\1\3", text, flags=re.DOTALL)

    return text


def process_file(path: Path) -> bool:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False
    cleaned = clean_text(raw)
    if cleaned != raw:
        path.write_text(cleaned, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    changed = []
    for target in TARGETS:
        if target.is_dir():
            for p in target.rglob("*.html"):
                if process_file(p):
                    changed.append(str(p.relative_to(ROOT)))
        elif target.is_file():
            if process_file(target):
                changed.append(str(target.relative_to(ROOT)))

    if changed:
        print("Updated files:\n - " + "\n - ".join(changed))
    else:
        print("No changes needed.")


if __name__ == "__main__":
    main()
