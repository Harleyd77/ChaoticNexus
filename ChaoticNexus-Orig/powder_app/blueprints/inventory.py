from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for

from ..core.db import connect, db_execute, db_query_all, db_query_one, get_db
from ..core.security import has_perm, is_admin, require_admin
from ..core.utils import to_float

bp = Blueprint("inventory", __name__)


@bp.route("/inventory")
def inventory_page():
    """Main inventory management page"""
    if not (is_admin() or has_perm("see_powders")):
        return redirect(url_for("auth.login", next=url_for("inventory.inventory_page")))

    # Get all powders with inventory data
    powders = db_query_all(
        """
        SELECT 
            id, powder_color, manufacturer, product_code, color_family,
            in_stock, on_hand_kg, last_weighed_kg, last_weighed_at,
            price_per_kg, weight_box_kg, charge_per_lb
        FROM powders 
        ORDER BY LOWER(powder_color) ASC
    """
    )

    # Calculate inventory status
    low_stock_threshold = 5.0  # kg
    out_of_stock = []
    low_stock = []
    in_stock = []

    for powder in powders:
        stock_kg = powder.get("on_hand_kg") or powder.get("in_stock") or 0
        if stock_kg <= 0:
            out_of_stock.append(powder)
        elif stock_kg <= low_stock_threshold:
            low_stock.append(powder)
        else:
            in_stock.append(powder)

    return render_template(
        "inventory.html",
        powders=powders,
        out_of_stock=out_of_stock,
        low_stock=low_stock,
        in_stock=in_stock,
        low_stock_threshold=low_stock_threshold,
        is_admin=is_admin(),
        total_powders=len(powders),
    )


@bp.route("/inventory/reorder")
def reorder_list():
    """Generate reorder list for low/out of stock items"""
    if not (is_admin() or has_perm("see_powders")):
        return redirect(url_for("auth.login", next=url_for("inventory.reorder_list")))

    # Get powders that need reordering
    reorder_items = db_query_all(
        """
        SELECT 
            id, powder_color, manufacturer, product_code, color_family,
            in_stock, on_hand_kg, weight_box_kg, price_per_kg,
            last_weighed_kg, last_weighed_at
        FROM powders 
        WHERE (on_hand_kg IS NULL OR on_hand_kg <= 5.0) 
           OR (in_stock IS NULL OR in_stock <= 5.0)
        ORDER BY 
            CASE WHEN (on_hand_kg IS NULL OR on_hand_kg <= 0) OR (in_stock IS NULL OR in_stock <= 0) THEN 0 ELSE 1 END,
            LOWER(powder_color) ASC
    """
    )

    return render_template(
        "reorder_list.html",
        reorder_items=reorder_items,
        is_admin=is_admin(),
        total_items=len(reorder_items),
    )


@bp.route("/inventory/<int:powder_id>/update", methods=["POST"])
def update_inventory(powder_id: int):
    """Update inventory levels for a powder"""
    guard = require_admin()
    if guard:
        return guard

    powder = db_query_one("SELECT * FROM powders WHERE id=?", (powder_id,))
    if not powder:
        abort(404)

    on_hand_kg = to_float(request.form.get("on_hand_kg"))
    notes = request.form.get("notes", "").strip()

    if on_hand_kg is None:
        flash("Please enter a valid weight.", "error")
        return redirect(url_for("inventory.inventory_page"))

    # Update inventory with timestamp
    db_execute(
        """
        UPDATE powders 
        SET on_hand_kg=?, last_weighed_kg=?, last_weighed_at=?
        WHERE id=?
    """,
        (on_hand_kg, on_hand_kg, datetime.now().isoformat(), powder_id),
    )

    # Log the inventory change
    db_execute(
        """
        INSERT INTO inventory_log (powder_id, change_type, old_value, new_value, notes, created_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            powder_id,
            "manual_update",
            powder.get("on_hand_kg"),
            on_hand_kg,
            notes,
            datetime.now().isoformat(),
            "admin",  # TODO: Get actual user
        ),
    )

    flash(f"Inventory updated for {powder['powder_color']}: {on_hand_kg} kg", "success")
    return redirect(url_for("inventory.inventory_page"))


@bp.route("/inventory/<int:powder_id>/adjust", methods=["POST"])
def adjust_inventory(powder_id: int):
    """Adjust inventory by adding or subtracting from current stock"""
    guard = require_admin()
    if guard:
        return guard

    powder = db_query_one("SELECT * FROM powders WHERE id=?", (powder_id,))
    if not powder:
        abort(404)

    adjustment = to_float(request.form.get("adjustment"))
    adjustment_type = request.form.get("adjustment_type", "add")
    notes = request.form.get("notes", "").strip()

    if adjustment is None:
        flash("Please enter a valid adjustment amount.", "error")
        return redirect(url_for("inventory.inventory_page"))

    current_stock = powder.get("on_hand_kg") or 0
    old_value = current_stock

    if adjustment_type == "subtract":
        new_value = max(0, current_stock - adjustment)
    else:  # add
        new_value = current_stock + adjustment

    # Update inventory
    db_execute(
        """
        UPDATE powders 
        SET on_hand_kg=?, last_weighed_kg=?, last_weighed_at=?
        WHERE id=?
    """,
        (new_value, new_value, datetime.now().isoformat(), powder_id),
    )

    # Log the adjustment
    db_execute(
        """
        INSERT INTO inventory_log (powder_id, change_type, old_value, new_value, notes, created_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            powder_id,
            f"adjustment_{adjustment_type}",
            old_value,
            new_value,
            notes,
            datetime.now().isoformat(),
            "admin",  # TODO: Get actual user
        ),
    )

    flash(
        f"Inventory adjusted for {powder['powder_color']}: {adjustment_type} {adjustment} kg",
        "success",
    )
    return redirect(url_for("inventory.inventory_page"))


@bp.route("/inventory/history/<int:powder_id>")
def inventory_history(powder_id: int):
    """Show inventory change history for a powder"""
    if not (is_admin() or has_perm("see_powders")):
        return redirect(
            url_for("auth.login", next=url_for("inventory.inventory_history", powder_id=powder_id))
        )

    powder = db_query_one("SELECT powder_color FROM powders WHERE id=?", (powder_id,))
    if not powder:
        abort(404)

    history = db_query_all(
        """
        SELECT * FROM inventory_log 
        WHERE powder_id=? 
        ORDER BY created_at DESC 
        LIMIT 50
    """,
        (powder_id,),
    )

    return render_template(
        "inventory_history.html", powder=powder, history=history, is_admin=is_admin()
    )


@bp.route("/inventory/api/powders")
def api_powders():
    """API endpoint for powder inventory data"""
    if not (is_admin() or has_perm("see_powders")):
        return jsonify({"error": "Unauthorized"}), 403

    powders = db_query_all(
        """
        SELECT 
            id, powder_color, manufacturer, product_code, color_family,
            in_stock, on_hand_kg, last_weighed_kg, last_weighed_at,
            price_per_kg, weight_box_kg, charge_per_lb
        FROM powders 
        ORDER BY LOWER(powder_color) ASC
    """
    )

    return jsonify(powders)


@bp.route("/inventory/api/update", methods=["POST"])
def api_update_inventory():
    """API endpoint for updating inventory"""
    guard = require_admin()
    if guard:
        return guard

    data = request.get_json()
    powder_id = data.get("powder_id")
    on_hand_kg = to_float(data.get("on_hand_kg"))

    if not powder_id or on_hand_kg is None:
        return jsonify({"error": "Invalid data"}), 400

    powder = db_query_one("SELECT powder_color FROM powders WHERE id=?", (powder_id,))
    if not powder:
        return jsonify({"error": "Powder not found"}), 404

    # Update inventory
    db_execute(
        """
        UPDATE powders 
        SET on_hand_kg=?, last_weighed_kg=?, last_weighed_at=?
        WHERE id=?
    """,
        (on_hand_kg, on_hand_kg, datetime.now().isoformat(), powder_id),
    )

    # Log the change
    db_execute(
        """
        INSERT INTO inventory_log (powder_id, change_type, old_value, new_value, notes, created_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            powder_id,
            "api_update",
            None,
            on_hand_kg,
            data.get("notes", ""),
            datetime.now().isoformat(),
            "api_user",
        ),
    )

    return jsonify(
        {
            "success": True,
            "message": f"Inventory updated for {powder['powder_color']}",
            "new_stock": on_hand_kg,
        }
    )


@bp.route("/inventory/api/reorder")
def api_reorder_list():
    """API endpoint for reorder list"""
    if not (is_admin() or has_perm("see_powders")):
        return jsonify({"error": "Unauthorized"}), 403

    reorder_items = db_query_all(
        """
        SELECT 
            id, powder_color, manufacturer, product_code, color_family,
            in_stock, on_hand_kg, weight_box_kg, price_per_kg
        FROM powders 
        WHERE (on_hand_kg IS NULL OR on_hand_kg <= 5.0) 
           OR (in_stock IS NULL OR in_stock <= 5.0)
        ORDER BY 
            CASE WHEN (on_hand_kg IS NULL OR on_hand_kg <= 0) OR (in_stock IS NULL OR in_stock <= 0) THEN 0 ELSE 1 END,
            LOWER(powder_color) ASC
    """
    )

    return jsonify(reorder_items)


def create_inventory_tables():
    """Create inventory-related database tables"""
    db = connect()

    # Create inventory_log table for tracking changes
    db.execute(
        """
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
    """
    )

    # Create reorder_settings table for configurable thresholds
    db.execute(
        """
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
    """
    )

    # Create index for performance
    db.execute("CREATE INDEX IF NOT EXISTS idx_inventory_log_powder_id ON inventory_log(powder_id)")
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_inventory_log_created_at ON inventory_log(created_at)"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_reorder_settings_powder_id ON reorder_settings(powder_id)"
    )

    db.commit()
    db.close()
