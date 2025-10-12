from __future__ import annotations

import os
import secrets
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:  # pragma: no cover - optional dependency
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BASE_DIR = PROJECT_ROOT
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", str(BASE_DIR / "storage")))
DATA_DIR = STORAGE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
UPLOADS_DIR = DATA_DIR / "uploads"

# Database configuration
DB_BACKEND = os.getenv("DB_BACKEND", "postgres").strip().lower()
if DB_BACKEND != "postgres":
    raise RuntimeError("PowderApp requires Postgres. Set DB_BACKEND=postgres and provide PG* connection settings.")
PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = int(os.getenv("PGPORT", "5432") or 5432)
PGDATABASE = os.getenv("PGDATABASE", "powderapp")
PGUSER = os.getenv("PGUSER", "powderapp")
PGPASSWORD = os.getenv("PGPASSWORD", "")

# Application defaults
DEPARTMENTS = ["unloading", "sandblaster", "prep", "sprayers", "finished"]
DEFAULT_FIRST_DEPT = "unloading"
ALLOWED_UPLOAD_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "heic", "heif", "pdf"}
ADMIN_PIN = os.getenv("ADMIN_PIN", "")


def configure_app(app) -> None:
    """Apply base Flask configuration shared across all environments."""
    secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(16)
    app.config["SECRET_KEY"] = secret_key
    app.config.setdefault("TEMPLATES_AUTO_RELOAD", True)
    app.config.setdefault("SEND_FILE_MAX_AGE_DEFAULT", 0)
    app.config.setdefault("JSON_AS_ASCII", False)
    try:
        app.jinja_env.charset = "utf-8"
        app.jinja_env.auto_reload = True
    except Exception:  # pragma: no cover - defensive
        pass