from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import DATA_DIR, DB_BACKEND, DB_PATH, PGDATABASE, PGHOST, PGPASSWORD, PGPORT, PGUSER, STORAGE_DIR, UPLOADS_DIR

try:
    import psycopg  # type: ignore
    from psycopg.rows import dict_row as _pg_dict_row  # type: ignore

    _HAVE_PG = True
except Exception:  # pragma: no cover - optional dependency
    _HAVE_PG = False

try:
    import psycopg.errors as _pg_err  # type: ignore

    _PG_INTEGRITY = _pg_err.UniqueViolation
except Exception:  # pragma: no cover
    _PG_INTEGRITY = None

try:
    _SQLITE_INTEGRITY = sqlite3.IntegrityError
except Exception:  # pragma: no cover - sqlite available on stdlib
    class _DummyExc(Exception):
        pass

    _SQLITE_INTEGRITY = _DummyExc

INTEGRITY_ERRORS = tuple(err for err in (_SQLITE_INTEGRITY, _PG_INTEGRITY) if err is not None)

_SQL_NOCASE_PATTERN = re.compile(r"([A-Za-z_][A-Za-z0-9_\.\"]*)\s+COLLATE\s+NOCASE", re.IGNORECASE)


def is_postgres() -> bool:
    return DB_BACKEND == "postgres"


def _translate_sql_for_pg(sql: str) -> tuple[str, bool]:
    statement = sql
    had_insert_ignore = False
    upper = statement.upper()
    if upper.strip().startswith("PRAGMA "):
        return ("SELECT 1", False)

    def _repl(match: re.Match[str]) -> str:
        column = match.group(1)
        return f"LOWER({column})"

    statement = _SQL_NOCASE_PATTERN.sub(_repl, statement)
    statement = re.sub(
        r"datetime\(\s*'now'\s*\)",
        "to_char(CURRENT_TIMESTAMP,'YYYY-MM-DD HH24:MI:SS')",
        statement,
        flags=re.IGNORECASE,
    )
    statement = re.sub(
        r"ROUND\(\(julianday\(([^\)]+)\)\-julianday\(([^\)]+)\)\)\*24\*60,\s*1\)",
        r"ROUND(EXTRACT(EPOCH FROM ((\1)::timestamp - (\2)::timestamp))/60.0, 1)",
        statement,
        flags=re.IGNORECASE,
    )
    if "INSERT OR IGNORE" in upper:
        had_insert_ignore = True
        statement = re.sub(r"(?i)INSERT\s+OR\s+IGNORE\s+INTO", "INSERT INTO", statement)
    return (statement, had_insert_ignore)


def _convert_params_for_pg(sql: str, params: tuple | list) -> tuple[str, tuple]:
    converted = sql.replace("?", "%s") if "?" in sql else sql
    if isinstance(params, list):
        params_tuple = tuple(params)
    elif isinstance(params, tuple):
        params_tuple = params
    else:
        params_tuple = (params,)
    return converted, params_tuple


class _PGResult:
    def __init__(self, cursor):
        self._cursor = cursor

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()




def _row_to_dict(row):
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    try:
        return dict(row)
    except TypeError:
        return row

class _PGConnection:
    def __init__(self):
        if not _HAVE_PG:
            raise RuntimeError(
                "psycopg not installed; cannot use Postgres backend. Install with: pip install psycopg[binary]"
            )
        self._conn = psycopg.connect(
            host=PGHOST,
            port=PGPORT,
            dbname=PGDATABASE,
            user=PGUSER,
            password=PGPASSWORD,
        )
        self._conn.autocommit = False

    def execute(self, sql: str, params: tuple | list = ()):  # mimic sqlite API
        translated, had_ignore = _translate_sql_for_pg(sql)
        translated, params_tuple = _convert_params_for_pg(translated, params)
        upper = translated.strip().upper()
        if had_ignore and upper.startswith("INSERT ") and " ON CONFLICT" not in upper:
            parts = translated.rsplit("RETURNING", 1)
            if len(parts) == 2:
                translated = parts[0].rstrip() + " ON CONFLICT DO NOTHING RETURNING" + parts[1]
            else:
                translated = translated.rstrip() + " ON CONFLICT DO NOTHING"
        cursor = self._conn.cursor(row_factory=_pg_dict_row)
        cursor.execute(translated, params_tuple)
        return _PGResult(cursor)

    def executescript(self, script: str):
        for statement in script.split(";"):
            if not statement.strip():
                continue
            normalized = statement.strip()
            if normalized.upper().startswith("PRAGMA "):
                continue
            self.execute(normalized)
        return self

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def cursor(self):  # pragma: no cover - compatibility shim
        return self


def connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    if not is_postgres():
        raise RuntimeError("PowderApp requires Postgres. Set DB_BACKEND=postgres.")
    return _PGConnection()


def get_db():
    return connect()


def _migrate_sqlite_schema(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()

    # TODO: Existing databases created while work_order_json was duplicated should have their schema checked manually.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            date_in TEXT,
            due_by TEXT,
            contact_name TEXT,
            company TEXT,
            phone TEXT,
            email TEXT,
            po TEXT,
            type TEXT,
            intake_source TEXT,
            priority TEXT,
            blast TEXT,
            prep TEXT,
            color TEXT,
            description TEXT,
            notes TEXT,
            status TEXT,
            department TEXT,
            completed_at TEXT,
            work_order_json TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS time_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            department TEXT NOT NULL,
            start_ts TEXT NOT NULL,
            end_ts TEXT,
            minutes INTEGER,
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS powders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            powder_color TEXT NOT NULL,
            manufacturer TEXT,
            product_code TEXT,
            gloss_level TEXT,
            finish TEXT,
            metallic INTEGER,
            needs_clear INTEGER,
            int_ext TEXT,
            additional_code TEXT,
            msds_url TEXT,
            sds_url TEXT,
            web_link TEXT,
            notes TEXT,
            additional_info TEXT,
            cure_schedule TEXT,
            price_per_kg REAL,
            charge_per_lb REAL,
            weight_box_kg REAL,
            last_price_check TEXT,
            in_stock REAL,
            shipping_cost REAL,
            picture_url TEXT
        )
        """
    )

    try:
        pow_cols = [row[1] for row in cursor.execute("PRAGMA table_info(powders)").fetchall()]
    except Exception:
        pow_cols = []
    for column, ddl in [
        ("color_family", "ALTER TABLE powders ADD COLUMN color_family TEXT"),
        ("aliases", "ALTER TABLE powders ADD COLUMN aliases TEXT"),
        ("additional_info", "ALTER TABLE powders ADD COLUMN additional_info TEXT"),
        ("cure_schedule", "ALTER TABLE powders ADD COLUMN cure_schedule TEXT"),
    ]:
        if column not in pow_cols:
            try:
                cursor.execute(ddl)
            except sqlite3.OperationalError:
                pass

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL UNIQUE,
            contact_name TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    for column, ddl in [
        ("street", "ALTER TABLE customers ADD COLUMN street TEXT"),
        ("city", "ALTER TABLE customers ADD COLUMN city TEXT"),
        ("region", "ALTER TABLE customers ADD COLUMN region TEXT"),
        ("postal_code", "ALTER TABLE customers ADD COLUMN postal_code TEXT"),
        ("country", "ALTER TABLE customers ADD COLUMN country TEXT"),
        ("website", "ALTER TABLE customers ADD COLUMN website TEXT"),
        ("tax_id", "ALTER TABLE customers ADD COLUMN tax_id TEXT"),
        ("account_number", "ALTER TABLE customers ADD COLUMN account_number TEXT"),
        ("terms", "ALTER TABLE customers ADD COLUMN terms TEXT"),
        ("status", "ALTER TABLE customers ADD COLUMN status TEXT"),
        ("phone_ext", "ALTER TABLE customers ADD COLUMN phone_ext TEXT"),
        ("updated_at", "ALTER TABLE customers ADD COLUMN updated_at TEXT"),
    ]:
        try:
            cursor.execute(ddl)
        except sqlite3.OperationalError:
            pass

    try:
        cols = [row[1] for row in cursor.execute("PRAGMA table_info(customers)").fetchall()]
    except Exception:
        cols = []
    if ("default_color" in cols) or ("default_prep" in cols):
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL UNIQUE,
                contact_name TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                street TEXT,
                city TEXT,
                region TEXT,
                postal_code TEXT,
                country TEXT,
                website TEXT,
                tax_id TEXT,
                account_number TEXT,
                terms TEXT,
                status TEXT,
                phone_ext TEXT,
                updated_at TEXT
            )
            """
        )
        cursor.execute(
            """
            INSERT INTO customers_new (
                id, company, contact_name, phone, email, address, notes, created_at,
                street, city, region, postal_code, country, website, tax_id, account_number, terms, status, phone_ext, updated_at
            )
            SELECT
                id, company, contact_name, phone, email, address, notes, created_at,
                street, city, region, postal_code, country, website, tax_id, account_number, terms, status, phone_ext, updated_at
            FROM customers
            """
        )
        cursor.execute("DROP TABLE customers")
        cursor.execute("ALTER TABLE customers_new RENAME TO customers")
        cursor.execute("PRAGMA foreign_keys=ON")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS job_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
        """
    )

    defaults = {
        "options": {
            "category": ["Railing", "Stairs", "Gates", "Fencing", "Other"],
            "blast": ["Light Etch", "Medium Etch", "Heavy Etch", "None"],
            "priority": ["Standard", "Semi Rush", "Rush", "Emergency"],
            "prep": ["Base /", "Full Prep", "Touch Up", "None Required"],
            "color_source": ["Non-stock color", "Customer supplied"],
        },
        "required": {
            "dateIn": True,
            "dueBy": False,
            "name": True,
            "company": True,
            "phone": True,
            "email": True,
            "category": True,
            "priority": True,
            "description": True,
            "prep": False,
            "blast": False,
            "color": False,
            "color_source": False,
            "po": False,
            "notes": False,
        },
    }
    cur = cursor.execute("SELECT value FROM settings WHERE name='intake_config'").fetchone()
    if not cur:
        cursor.execute(
            "INSERT INTO settings (name, value) VALUES (?,?)",
            ("intake_config", json.dumps(defaults)),
        )

    cur = cursor.execute("SELECT value FROM settings WHERE name='ui_settings'").fetchone()
    if not cur:
        cursor.execute(
            "INSERT INTO settings (name, value) VALUES (?,?)",
            ("ui_settings", json.dumps({"show_csv": False})),
        )

    for ddl in [
        "ALTER TABLE jobs ADD COLUMN intake_source TEXT",
        "ALTER TABLE jobs ADD COLUMN archived INTEGER DEFAULT 0",
        "ALTER TABLE jobs ADD COLUMN archived_reason TEXT",
        "ALTER TABLE jobs ADD COLUMN color_source TEXT",
        "ALTER TABLE jobs ADD COLUMN blast TEXT",
        "ALTER TABLE jobs ADD COLUMN completed_at TEXT",
        "ALTER TABLE jobs ADD COLUMN order_index INTEGER",
        "ALTER TABLE jobs ADD COLUMN on_screen INTEGER DEFAULT 0",
        "ALTER TABLE jobs ADD COLUMN screen_order_index INTEGER",
        "ALTER TABLE jobs ADD COLUMN work_order_json TEXT",
    ]:
        try:
            cursor.execute(ddl)
        except sqlite3.OperationalError:
            pass

    try:
        cursor.execute("UPDATE jobs SET archived=0 WHERE archived IS NULL")
    except Exception:
        pass

    try:
        cursor.execute(
            "UPDATE jobs SET intake_source='railing' WHERE intake_source IS NULL AND lower(COALESCE(type,''))='railing'"
        )
        cursor.execute(
            "UPDATE jobs SET intake_source='production' WHERE intake_source IS NULL"
        )
    except Exception:
        pass

    connection.commit()

    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(lower(company))")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_contact ON jobs(lower(contact_name))")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_color ON jobs(lower(color))")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_description ON jobs(lower(description))")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_intake_source ON jobs(intake_source)")
    except Exception:
        pass

    try:
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_company_norm
            ON customers (lower(trim(company)))
            """
        )
    except Exception:
        pass

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            name TEXT,
            phone TEXT,
            ext TEXT,
            email TEXT,
            role TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            permissions_json TEXT
        )
        """
    )

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN permissions_json TEXT")
    except sqlite3.OperationalError:
        pass

    connection.commit()


def init_db():
    if not is_postgres():
        raise RuntimeError("PowderApp requires Postgres. Set DB_BACKEND=postgres.")
    return init_db_postgres()


def init_db_postgres():  # pragma: no cover - requires Postgres
    db = connect()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
        """
    )
    # Create customer_accounts first since jobs references it
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS customer_accounts (
            id SERIAL PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            company_name TEXT,
            phone TEXT,
            created_at TEXT NOT NULL,
            last_login TEXT,
            is_active INTEGER DEFAULT 1,
            reset_token TEXT,
            reset_token_expires TEXT
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            created_at TEXT NOT NULL,
            date_in TEXT,
            due_by TEXT,
            contact_name TEXT,
            company TEXT,
            phone TEXT,
            email TEXT,
            po TEXT,
            type TEXT,
            intake_source TEXT,
            priority TEXT,
            blast TEXT,
            prep TEXT,
            color TEXT,
            color_source TEXT,
            description TEXT,
            notes TEXT,
            status TEXT,
            department TEXT,
            completed_at TEXT,
            work_order_json TEXT,
            archived INTEGER DEFAULT 0,
            archived_reason TEXT,
            order_index INTEGER,
            on_screen INTEGER DEFAULT 0,
            screen_order_index INTEGER,
            customer_account_id INTEGER,
            submitted_by_customer INTEGER DEFAULT 0,
            requires_approval INTEGER DEFAULT 0,
            FOREIGN KEY(customer_account_id) REFERENCES customer_accounts(id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS time_logs (
            id SERIAL PRIMARY KEY,
            job_id INTEGER NOT NULL,
            department TEXT NOT NULL,
            start_ts TEXT NOT NULL,
            end_ts TEXT,
            minutes INTEGER,
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS powders (
            id SERIAL PRIMARY KEY,
            created_at TEXT NOT NULL,
            powder_color TEXT NOT NULL,
            manufacturer TEXT,
            product_code TEXT,
            gloss_level TEXT,
            finish TEXT,
            metallic INTEGER,
            needs_clear INTEGER,
            int_ext TEXT,
            additional_code TEXT,
            msds_url TEXT,
            sds_url TEXT,
            web_link TEXT,
            notes TEXT,
            additional_info TEXT,
            cure_schedule TEXT,
            price_per_kg REAL,
            charge_per_lb REAL,
            weight_box_kg REAL,
            last_price_check TEXT,
            in_stock REAL,
            shipping_cost REAL,
            picture_url TEXT,
            color_family TEXT,
            aliases TEXT,
            on_hand_kg REAL,
            last_weighed_kg REAL,
            last_weighed_at TEXT
        )
        """
    )
    has_cure = db.execute("SELECT 1 FROM information_schema.columns WHERE table_name='powders' AND column_name='cure_schedule'").fetchone()
    if not has_cure:
        db.execute("ALTER TABLE powders ADD COLUMN cure_schedule TEXT")

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            company TEXT NOT NULL UNIQUE,
            contact_name TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            street TEXT,
            city TEXT,
            region TEXT,
            postal_code TEXT,
            country TEXT,
            website TEXT,
            tax_id TEXT,
            account_number TEXT,
            terms TEXT,
            status TEXT,
            phone_ext TEXT,
            updated_at TEXT
        )
        """
    )
    db.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_company_norm
        ON customers (lower(trim(company)))
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            name TEXT,
            phone TEXT,
            ext TEXT,
            email TEXT,
            role TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            permissions_json TEXT
        )
        """
    )
    has_perm_column = db.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='permissions_json'"
    ).fetchone()
    if not has_perm_column:
        db.execute("ALTER TABLE users ADD COLUMN permissions_json TEXT")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS job_photos (
            id SERIAL PRIMARY KEY,
            job_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
        """
    )
    # customer_accounts already created above before jobs table
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS job_edit_history (
            id SERIAL PRIMARY KEY,
            job_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            change_reason TEXT,
            created_at TEXT NOT NULL DEFAULT (to_char(CURRENT_TIMESTAMP,'YYYY-MM-DD HH24:MI:SS')),
            FOREIGN KEY(job_id) REFERENCES jobs(id),
            FOREIGN KEY(customer_id) REFERENCES customer_accounts(id)
        )
        """
    )
    # Check and add missing columns to jobs table
    has_customer_account_id = db.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name='jobs' AND column_name='customer_account_id'"
    ).fetchone()
    if not has_customer_account_id:
        db.execute("ALTER TABLE jobs ADD COLUMN customer_account_id INTEGER")
        db.execute("ALTER TABLE jobs ADD COLUMN submitted_by_customer INTEGER DEFAULT 0")
        db.execute("ALTER TABLE jobs ADD COLUMN requires_approval INTEGER DEFAULT 0")

    has_intake_source = db.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name='jobs' AND column_name='intake_source'"
    ).fetchone()
    if not has_intake_source:
        db.execute("ALTER TABLE jobs ADD COLUMN intake_source TEXT")

    try:
        db.execute(
            "UPDATE jobs SET intake_source='railing' WHERE intake_source IS NULL AND lower(COALESCE(type,''))='railing'"
        )
        db.execute("UPDATE jobs SET intake_source='production' WHERE intake_source IS NULL")
    except Exception:
        pass

    # Create indexes with error handling for concurrent access
    # Note: indexes for inventory_log and reorder_settings created after those tables below
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(lower(company))",
        "CREATE INDEX IF NOT EXISTS idx_jobs_contact ON jobs(lower(contact_name))",
        "CREATE INDEX IF NOT EXISTS idx_jobs_color ON jobs(lower(color))",
        "CREATE INDEX IF NOT EXISTS idx_jobs_description ON jobs(lower(description))",
        "CREATE INDEX IF NOT EXISTS idx_jobs_intake_source ON jobs(intake_source)",
        "CREATE INDEX IF NOT EXISTS idx_jobs_customer_account ON jobs(customer_account_id)",
        "CREATE INDEX IF NOT EXISTS idx_customer_accounts_email ON customer_accounts(lower(email))",
        "CREATE INDEX IF NOT EXISTS idx_job_edit_history_job_id ON job_edit_history(job_id)",
        "CREATE INDEX IF NOT EXISTS idx_job_edit_history_customer_id ON job_edit_history(customer_id)"
    ]
    
    for index_sql in indexes:
        try:
            db.execute(index_sql)
        except Exception as e:
            # Ignore errors for concurrent index creation
            if "already exists" in str(e) or "deadlock" in str(e).lower():
                pass
            else:
                print(f"Warning: Could not create index: {e}")

    # Print templates table for saving custom print layouts
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS print_templates (
            id SERIAL PRIMARY KEY,
            template_type TEXT NOT NULL,
            template_name TEXT NOT NULL,
            layout_json TEXT NOT NULL,
            is_default INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            created_by TEXT,
            UNIQUE(template_type, template_name)
        )
        """
    )
    db.execute("CREATE INDEX IF NOT EXISTS idx_print_templates_type ON print_templates(template_type)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_print_templates_default ON print_templates(template_type, is_default)")

    # Create inventory management tables
    db.execute("""
        CREATE TABLE IF NOT EXISTS inventory_log (
            id SERIAL PRIMARY KEY,
            powder_id INTEGER NOT NULL,
            change_type TEXT NOT NULL,
            old_value REAL,
            new_value REAL,
            notes TEXT,
            created_at TEXT NOT NULL,
            created_by TEXT,
            FOREIGN KEY(powder_id) REFERENCES powders(id)
        )
    """)
    
    db.execute("""
        CREATE TABLE IF NOT EXISTS reorder_settings (
            id SERIAL PRIMARY KEY,
            powder_id INTEGER,
            low_stock_threshold REAL DEFAULT 5.0,
            reorder_quantity REAL,
            supplier_info TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY(powder_id) REFERENCES powders(id)
        )
    """)
    
    # Create indexes for inventory tables (after tables exist)
    db.execute("CREATE INDEX IF NOT EXISTS idx_inventory_log_powder_id ON inventory_log(powder_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_inventory_log_created_at ON inventory_log(created_at)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_reorder_settings_powder_id ON reorder_settings(powder_id)")

    cur = db.execute("SELECT value FROM settings WHERE name='intake_config'").fetchone()
    if not cur:
        defaults = {
            "options": {
                "category": ["Railing", "Stairs", "Gates", "Fencing", "Other"],
                "blast": ["Light Etch", "Medium Etch", "Heavy Etch", "None"],
                "priority": ["Standard", "Semi Rush", "Rush", "Emergency"],
                "prep": ["Base /", "Full Prep", "Touch Up", "None Required"],
                "color_source": ["Non-stock color", "Customer supplied"],
            },
            "required": {
                "dateIn": True,
                "dueBy": False,
                "name": True,
                "company": True,
                "phone": True,
                "email": True,
                "category": True,
                "priority": True,
                "description": True,
                "prep": False,
                "blast": False,
                "color": False,
                "color_source": False,
                "po": False,
                "notes": False,
            },
        }
        db.execute(
            "INSERT INTO settings (name, value) VALUES (?,?)",
            ("intake_config", json.dumps(defaults)),
        )
    cur = db.execute("SELECT value FROM settings WHERE name='ui_settings'").fetchone()
    if not cur:
        db.execute(
            "INSERT INTO settings (name, value) VALUES (?,?)",
            ("ui_settings", json.dumps({"show_csv": False})),
        )

    db.commit()
    db.close()


def db_execute(query: str, params: Any = ()):  # type: ignore[override]
    conn = connect()
    conn.execute(query, params)
    conn.commit()
    conn.close()


def db_query_all(query: str, params: Any = ()):  # type: ignore[override]
    conn = connect()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_dict(row) for row in rows]


def db_query_one(query: str, params: Any = ()):  # type: ignore[override]
    conn = connect()
    row = conn.execute(query, params).fetchone()
    conn.close()
    return _row_to_dict(row)


def get_ui_settings() -> dict:
    row = db_query_one("SELECT value FROM settings WHERE name='ui_settings'")
    ui = {"show_csv": False}
    if row:
        try:
            ui.update(json.loads(row["value"]))
        except Exception:
            pass
    return ui


def save_ui_settings(ui: dict) -> None:
    exists = db_query_one("SELECT id FROM settings WHERE name='ui_settings'")
    value = json.dumps(ui)
    if exists:
        db_execute("UPDATE settings SET value=? WHERE name='ui_settings'", (value,))
    else:
        db_execute("INSERT INTO settings (name,value) VALUES (?,?)", ("ui_settings", value))


try:  # Startup diagnostics for container mis-mounts
    print(f"[PowderApp] Using DB: {DB_PATH}")
    stray = Path("/app/data/app.db")
    if stray.exists() and stray.resolve() != Path(DB_PATH).resolve():
        print(
            "[PowderApp][WARN] Found stray DB at /app/data/app.db but app uses /app/storage/data/app.db.\n"
            "Ensure your container path mapping uses /app/storage/data, not /app/data."
        )
except Exception:
    pass

