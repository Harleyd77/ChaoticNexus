"""Simple migration endpoint for adding database columns"""

from flask import Blueprint, jsonify

from ..core.db import db_execute, db_query_one, is_postgres
from ..core.security import require_admin

bp = Blueprint("migrate", __name__)


@bp.route("/admin/migrate/add-charge-columns")
def add_charge_columns():
    """Add charge_per_kg and charge_per_lb columns to powders table"""
    guard = require_admin()
    if guard:
        return guard

    results = []

    try:
        # Check if columns exist by trying to query them
        try:
            db_query_one("SELECT charge_per_kg, charge_per_lb FROM powders LIMIT 1")
            results.append("✓ Columns already exist - no migration needed")
            return jsonify({"success": True, "results": results})
        except Exception:
            # Columns don't exist, need to add them
            pass

        # Add charge_per_kg column
        try:
            if is_postgres():
                db_execute("ALTER TABLE powders ADD COLUMN IF NOT EXISTS charge_per_kg REAL")
            else:
                db_execute("ALTER TABLE powders ADD COLUMN charge_per_kg REAL")
            results.append("✓ Added charge_per_kg column")
        except Exception as e:
            if "duplicate column" not in str(e).lower() and "already exists" not in str(e).lower():
                results.append(f"⚠ charge_per_kg: {e}")
            else:
                results.append("✓ charge_per_kg already exists")

        # Add charge_per_lb column
        try:
            if is_postgres():
                db_execute("ALTER TABLE powders ADD COLUMN IF NOT EXISTS charge_per_lb REAL")
            else:
                db_execute("ALTER TABLE powders ADD COLUMN charge_per_lb REAL")
            results.append("✓ Added charge_per_lb column")
        except Exception as e:
            if "duplicate column" not in str(e).lower() and "already exists" not in str(e).lower():
                results.append(f"⚠ charge_per_lb: {e}")
            else:
                results.append("✓ charge_per_lb already exists")

        results.append("\n✅ Migration completed!")
        results.append("Note: Existing powders will have NULL values.")
        results.append("Edit and save each powder to populate the charge values.")

        return jsonify({"success": True, "results": results})

    except Exception as e:
        results.append(f"❌ Migration failed: {e}")
        return jsonify({"success": False, "results": results}), 500
