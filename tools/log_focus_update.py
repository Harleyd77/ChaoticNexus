#!/usr/bin/env python3
"""Append timestamped notes to project documentation.

Currently targets `docs/current-focus.md` by inserting a dated bullet under the
"Recently Completed" section and refreshing the "Last updated" stamp. Run this
script after finishing a cleanup task to keep the working plan in sync.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_MAP = {
    "current": ROOT / "docs" / "current-focus.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log a timestamped note to docs/current-focus.md",
    )
    parser.add_argument(
        "summary",
        nargs="?",
        help="Summary of the change to log (prompted if omitted)",
    )
    parser.add_argument(
        "--doc",
        choices=DOCS_MAP.keys(),
        default="current",
        help="Documentation target to update (default: current)",
    )
    return parser.parse_args()


def prompt_for_summary() -> str:
    try:
        return input("What changed? ").strip()
    except EOFError:  # pragma: no cover - interactive convenience
        return ""


def update_current_focus(doc_path: Path, summary: str) -> None:
    if not doc_path.exists():
        raise SystemExit(f"Document not found: {doc_path}")

    today = date.today().strftime("%B %d, %Y")
    lines = doc_path.read_text(encoding="utf-8").splitlines()

    # Refresh the "Last updated" stamp if present.
    for idx, line in enumerate(lines):
        if line.startswith("_Last updated:"):
            lines[idx] = f"_Last updated: {today}_"
            break

    try:
        header_idx = lines.index("## Recently Completed")
    except ValueError as exc:  # pragma: no cover - defensive
        raise SystemExit("Section '## Recently Completed' not found") from exc

    insert_idx = header_idx + 1

    # Ensure a blank line exists after the header for readability.
    if insert_idx >= len(lines) or lines[insert_idx].strip():
        lines.insert(insert_idx, "")
        insert_idx += 1
    else:
        insert_idx += 1

    # Skip placeholder text and extra blank lines.
    while insert_idx < len(lines) and not lines[insert_idx].strip():
        insert_idx += 1

    if insert_idx < len(lines) and "None yet" in lines[insert_idx]:
        del lines[insert_idx]

    entry_line = f"- {today}: {summary}"
    lines.insert(insert_idx, entry_line)

    doc_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    summary = args.summary.strip() if args.summary else prompt_for_summary()
    if not summary:
        raise SystemExit("Aborted: summary is required.")

    doc_path = DOCS_MAP[args.doc]
    update_current_focus(doc_path, summary)
    print(f"Logged entry to {doc_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
