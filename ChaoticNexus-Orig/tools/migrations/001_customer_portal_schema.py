#!/usr/bin/env python3
"""
Migration: Add customer portal schema

This migration adds tables and columns needed for the customer portal feature:
- customer_accounts: Customer login accounts
- customer_sessions: Session management
- job_edit_history: Audit trail for job changes
- Additional columns on jobs table for customer ownership
"""

import sqlite3
from pathlib import Path


def run_migration(db_path: str) -> None:
    """Run the customer portal schema migration."""
    print(f"Running customer portal migration on {db_path}")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Create customer_accounts table
        print("Creating customer_accounts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                company_name VARCHAR(255),
                phone VARCHAR(50),
                address TEXT,
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create customer_sessions table
        print("Creating customer_sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                session_token VARCHAR(255) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY(customer_id) REFERENCES customer_accounts(id) ON DELETE CASCADE
            )
        """)

        # Create job_edit_history table
        print("Creating job_edit_history table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_edit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                customer_id INTEGER,
                field_name VARCHAR(100) NOT NULL,
                old_value TEXT,
                new_value TEXT,
                change_reason TEXT,
                changed_by_customer BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE,
                FOREIGN KEY(customer_id) REFERENCES customer_accounts(id) ON DELETE SET NULL
            )
        """)

        # Add customer portal columns to jobs table
        print("Adding customer portal columns to jobs table...")
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN customer_account_id INTEGER REFERENCES customer_accounts(id)")
        except sqlite3.OperationalError:
            print("  Column customer_account_id already exists")

        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN submitted_by_customer BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            print("  Column submitted_by_customer already exists")

        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN requires_approval BOOLEAN DEFAULT 1")
        except sqlite3.OperationalError:
            print("  Column requires_approval already exists")

        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN customer_notes TEXT")
        except sqlite3.OperationalError:
            print("  Column customer_notes already exists")

        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN shop_notes TEXT")
        except sqlite3.OperationalError:
            print("  Column shop_notes already exists")

        # Create indexes for performance
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_accounts_email ON customer_accounts(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_sessions_token ON customer_sessions(session_token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_sessions_customer_id ON customer_sessions(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_edit_history_job_id ON job_edit_history(job_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_edit_history_customer_id ON job_edit_history(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_customer_account_id ON jobs(customer_account_id)")

        conn.commit()
        print("✅ Customer portal migration completed successfully!")


def rollback_migration(db_path: str) -> None:
    """Rollback the customer portal migration."""
    print(f"Rolling back customer portal migration on {db_path}")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Drop tables (this will cascade delete related records)
        tables_to_drop = ['job_edit_history', 'customer_sessions', 'customer_accounts']

        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"  Dropped table: {table}")
            except sqlite3.OperationalError as e:
                print(f"  Warning: Could not drop table {table}: {e}")

        # Remove columns from jobs table (SQLite doesn't support DROP COLUMN easily)
        # We'll leave the columns but they won't be used after rollback
        print("  Note: Customer portal columns remain in jobs table but are unused")

        conn.commit()
        print("✅ Rollback completed!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python 001_customer_portal_schema.py <db_path> <run|rollback>")
        sys.exit(1)

    db_path = sys.argv[1]
    action = sys.argv[2]

    if not Path(db_path).exists():
        print(f"Error: Database file {db_path} does not exist")
        sys.exit(1)

    if action == "run":
        run_migration(db_path)
    elif action == "rollback":
        rollback_migration(db_path)
    else:
        print("Error: Action must be 'run' or 'rollback'")
        sys.exit(1)
