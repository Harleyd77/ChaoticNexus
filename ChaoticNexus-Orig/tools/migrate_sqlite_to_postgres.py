#!/usr/bin/env python3
import os
import argparse
import sqlite3
from typing import Iterable

try:
    import psycopg
except Exception as e:
    print("psycopg is required. Install with: pip install psycopg[binary]")
    raise


DDL_CORE = [
    # settings
    """
    CREATE TABLE IF NOT EXISTS settings (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        value TEXT NOT NULL
    )
    """,
    # jobs
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
        archived INTEGER DEFAULT 0,
        archived_reason TEXT,
        order_index INTEGER,
        on_screen INTEGER DEFAULT 0,
        screen_order_index INTEGER
    )
    """,
    # time_logs
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
    """,
    # powders
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
    """,
    # customers
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
    """,
    # unique index for normalized company
    """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_company_norm
    ON customers (lower(trim(company)))
    """,
    # contacts
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
    """,
    # users
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        permissions_json TEXT
    )
    """,
    # job_photos
    """
    CREATE TABLE IF NOT EXISTS job_photos (
        id SERIAL PRIMARY KEY,
        job_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        original_name TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    """,
]

DDL_SPRAYER = [
    """
    CREATE TABLE IF NOT EXISTS job_powders (
      job_id    INTEGER NOT NULL,
      powder_id INTEGER NOT NULL,
      role      TEXT DEFAULT 'primary',
      est_kg    REAL,
      PRIMARY KEY (job_id, powder_id, role),
      FOREIGN KEY (job_id)    REFERENCES jobs(id)    ON DELETE CASCADE,
      FOREIGN KEY (powder_id) REFERENCES powders(id) ON DELETE RESTRICT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS spray_batch (
      id               SERIAL PRIMARY KEY,
      powder_id        INTEGER NOT NULL,
      role             TEXT DEFAULT 'primary',
      operator         TEXT,
      note             TEXT,
      started_at       TEXT NOT NULL DEFAULT to_char(CURRENT_TIMESTAMP,'YYYY-MM-DD HH24:MI:SS'),
      ended_at         TEXT,
      start_weight_kg  REAL NOT NULL,
      end_weight_kg    REAL,
      used_kg          REAL,
      duration_min     REAL,
      FOREIGN KEY (powder_id) REFERENCES powders(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS spray_batch_jobs (
      batch_id   INTEGER NOT NULL,
      job_id     INTEGER NOT NULL,
      time_min   REAL,
      start_ts   TEXT,
      end_ts     TEXT,
      PRIMARY KEY (batch_id, job_id),
      FOREIGN KEY (batch_id) REFERENCES spray_batch(id) ON DELETE CASCADE,
      FOREIGN KEY (job_id)    REFERENCES jobs(id)       ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS powder_usage (
      id         SERIAL PRIMARY KEY,
      powder_id  INTEGER NOT NULL,
      job_id     INTEGER,
      used_kg    REAL NOT NULL,
      note       TEXT,
      created_at TEXT NOT NULL DEFAULT to_char(CURRENT_TIMESTAMP,'YYYY-MM-DD HH24:MI:SS'),
      FOREIGN KEY (powder_id) REFERENCES powders(id),
      FOREIGN KEY (job_id)    REFERENCES jobs(id)
    )
    """,
]


def run_sql_list(cur, ddls: Iterable[str]):
    for ddl in ddls:
        cur.execute(ddl)


def copy_table(cur_pg, cur_sq, table: str, columns: list[str], conflict_cols: list[str] | None = None):
    cols_csv = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    conflict = ""
    if conflict_cols:
        conflict = f" ON CONFLICT ({', '.join(conflict_cols)}) DO NOTHING"
    cur_sq.execute(f"SELECT {cols_csv} FROM {table}")
    rows = cur_sq.fetchall()
    for r in rows:
        vals = [r[c] for c in columns]
        cur_pg.execute(f"INSERT INTO {table} ({cols_csv}) VALUES ({placeholders}){conflict}", vals)


def set_serial(cur, table: str, col: str = "id"):
    cur.execute("SELECT setval(pg_get_serial_sequence(%s,%s), COALESCE((SELECT MAX(" + col + ") FROM " + table + "), 1), TRUE)", (table, col))


def main():
    ap = argparse.ArgumentParser(description="Migrate SQLite data to Postgres for PowderApp")
    ap.add_argument("--sqlite", default=os.path.join("storage", "data", "app.db"))
    ap.add_argument("--host", default=os.getenv("PGHOST", "localhost"))
    ap.add_argument("--port", type=int, default=int(os.getenv("PGPORT", "5432")))
    ap.add_argument("--db", default=os.getenv("PGDATABASE", "powderapp"))
    ap.add_argument("--user", default=os.getenv("PGUSER", "powderapp"))
    ap.add_argument("--password", default=os.getenv("PGPASSWORD", ""))
    args = ap.parse_args()

    if not os.path.exists(args.sqlite):
        raise SystemExit(f"SQLite file not found: {args.sqlite}")

    sq = sqlite3.connect(args.sqlite)
    sq.row_factory = sqlite3.Row
    pg = psycopg.connect(host=args.host, port=args.port, dbname=args.db, user=args.user, password=args.password)
    pg.autocommit = False
    try:
        with pg.cursor() as cpg:
            # Create schema
            run_sql_list(cpg, DDL_CORE)
            run_sql_list(cpg, DDL_SPRAYER)

            csq = sq.cursor()
            # Copy base tables
            copy_table(cpg, csq, "settings", ["id","name","value"], conflict_cols=["id"]) 
            copy_table(cpg, csq, "users",    ["id","username","password_hash","is_admin","created_at","permissions_json"], conflict_cols=["id"]) 
            copy_table(cpg, csq, "customers", [
                "id","company","contact_name","phone","email","address","notes","created_at",
                "street","city","region","postal_code","country","website","tax_id","account_number",
                "terms","status","phone_ext","updated_at"
            ], conflict_cols=["id"]) 
            copy_table(cpg, csq, "powders",   [
                "id","created_at","powder_color","manufacturer","product_code","gloss_level","finish",
                "metallic","needs_clear","int_ext","additional_code","msds_url","sds_url","web_link","notes","additional_info","cure_schedule",
                "price_per_kg","charge_per_lb","weight_box_kg","last_price_check","in_stock","shipping_cost",
                "picture_url","color_family","aliases","on_hand_kg","last_weighed_kg","last_weighed_at"
            ], conflict_cols=["id"]) 
            copy_table(cpg, csq, "jobs",      [
                "id","created_at","date_in","due_by","contact_name","company","phone","email","po","type",
                "priority","blast","prep","color","color_source","description","notes","status","department",
                "completed_at","archived","archived_reason","order_index","on_screen","screen_order_index"
            ], conflict_cols=["id"]) 
            copy_table(cpg, csq, "contacts",  [
                "id","customer_id","name","phone","ext","email","role","notes","created_at","updated_at"
            ], conflict_cols=["id"]) 
            copy_table(cpg, csq, "time_logs", ["id","job_id","department","start_ts","end_ts","minutes"], conflict_cols=["id"]) 
            copy_table(cpg, csq, "job_photos", ["id","job_id","filename","original_name","created_at"], conflict_cols=["id"]) 
            # Sprayer-related
            copy_table(cpg, csq, "job_powders", ["job_id","powder_id","role","est_kg"], conflict_cols=["job_id","powder_id","role"]) 
            copy_table(cpg, csq, "spray_batch", [
                "id","powder_id","role","operator","note","started_at","ended_at","start_weight_kg","end_weight_kg","used_kg","duration_min"
            ], conflict_cols=["id"]) 
            copy_table(cpg, csq, "spray_batch_jobs", ["batch_id","job_id","time_min","start_ts","end_ts"], conflict_cols=["batch_id","job_id"]) 
            copy_table(cpg, csq, "powder_usage", ["id","powder_id","job_id","used_kg","note","created_at"], conflict_cols=["id"]) 

            # Fix sequences
            for table in ["settings","users","customers","powders","jobs","contacts","time_logs","job_photos","spray_batch","powder_usage"]:
                set_serial(cpg, table, "id")

        pg.commit()
        print("Migration complete.")
    except Exception:
        pg.rollback()
        raise
    finally:
        pg.close()
        sq.close()


if __name__ == "__main__":
    main()

