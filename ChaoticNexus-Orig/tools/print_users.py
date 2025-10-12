"""List application users using the Postgres backend."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DB_BACKEND", "postgres")
sys.path.insert(0, str(ROOT / "src"))

from powder_app.core import db  # noqa: E402


def main() -> None:
    rows = db.db_query_all(
        "SELECT id, username, is_admin, created_at FROM users ORDER BY username"
    )
    if not rows:
        print("No users found.")
        return
    for row in rows:
        print(
            f"{row['id']:>4} | {row['username']:<20} | "
            f"admin={'yes' if row['is_admin'] else 'no'} | created={row['created_at']}"
        )


if __name__ == "__main__":
    main()
