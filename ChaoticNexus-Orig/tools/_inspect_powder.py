"""Inspect powders via the Postgres backend."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DB_BACKEND", "postgres")
sys.path.insert(0, str(ROOT / "src"))

from powder_app.core import db  # noqa: E402


def main() -> None:
    query = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
    if query:
        rows = db.db_query_all(
            """
            SELECT id, powder_color, color_family, aliases, manufacturer, product_code
            FROM powders
            WHERE lower(powder_color) LIKE ?
               OR lower(product_code) LIKE ?
               OR lower(color_family) LIKE ?
            ORDER BY powder_color
            """,
            (f"%{query}%", f"%{query}%", f"%{query}%"),
        )
    else:
        rows = db.db_query_all(
            "SELECT id, powder_color, color_family, aliases, manufacturer, product_code FROM powders ORDER BY powder_color LIMIT 20"
        )
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
