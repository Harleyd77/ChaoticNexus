"""Create or update an admin user using the Postgres backend."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from werkzeug.security import generate_password_hash
except Exception:
    generate_password_hash = None

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DB_BACKEND", "postgres")
sys.path.insert(0, str(ROOT / "src"))

from powder_app.core import db  # noqa: E402


def main() -> None:
    username = os.environ.get("UNLOCK_USER", "admin")
    password = os.environ.get("UNLOCK_PASS", "changeme123")
    now = datetime.utcnow().isoformat()

    if generate_password_hash:
        pw_hash = generate_password_hash(password)
    else:
        pw_hash = password

    existing = db.db_query_one("SELECT id FROM users WHERE username=?", (username,))
    if existing:
        db.db_execute(
            "UPDATE users SET is_admin=1, password_hash=?, permissions_json=permissions_json, created_at=created_at WHERE id=?",
            (pw_hash, existing["id"]),
        )
        action = f"updated existing user '{username}' to admin"
    else:
        db.db_execute(
            "INSERT INTO users (username, password_hash, is_admin, created_at, permissions_json) VALUES (?,?,?,?,?)",
            (username, pw_hash, 1, now, None),
        )
        action = f"created admin user '{username}'"

    print(f"OK: {action}. You can now log in with {username}/{password}.")


if __name__ == "__main__":
    main()
