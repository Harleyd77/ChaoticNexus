"""
Blueprint for managing print templates.
Allows saving, loading, and managing different print layouts for various form types.
"""

from __future__ import annotations

import json
from datetime import datetime

from flask import Blueprint, jsonify, request

from ..core.db import connect, db_execute, db_query_one
from ..core.security import get_current_username, is_admin

bp = Blueprint("print_templates", __name__)


FALLBACK_TEMPLATES = {
    "job_worksheet_production": ["job_worksheet"],
    "job_worksheet_railing": ["job_worksheet_production", "job_worksheet"],
}


def _fetch_template_row(conn, template_type: str):
    row = conn.execute(
        """
        SELECT id, template_type, template_name, layout_json, is_default, created_at, updated_at
        FROM print_templates
        WHERE template_type = ? AND is_default = 1
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (template_type,),
    ).fetchone()
    if row:
        return row
    return conn.execute(
        """
        SELECT id, template_type, template_name, layout_json, is_default, created_at, updated_at
        FROM print_templates
        WHERE template_type = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (template_type,),
    ).fetchone()


@bp.route("/api/print-templates/<template_type>", methods=["GET"])
def get_template(template_type):
    """Get the default template for a specific type."""
    conn = connect()
    try:
        candidates = [template_type]
        fallback = FALLBACK_TEMPLATES.get(template_type)
        if fallback:
            candidates.extend(fallback)

        row = None
        for candidate in candidates:
            row = _fetch_template_row(conn, candidate)
            if row:
                break

        if row:
            return jsonify(
                {
                    "success": True,
                    "template": {
                        "id": row["id"],
                        "template_type": row["template_type"],
                        "template_name": row["template_name"],
                        "layout": json.loads(row["layout_json"]),
                        "is_default": bool(row["is_default"]),
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                    },
                }
            )
        return jsonify({"success": True, "template": None})
    finally:
        conn.close()


@bp.route("/api/print-templates/<template_type>/all", methods=["GET"])
def list_templates(template_type):
    """List all templates for a specific type."""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403

    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT id, template_type, template_name, is_default, created_at, updated_at, created_by
            FROM print_templates
            WHERE template_type = ?
            ORDER BY is_default DESC, updated_at DESC
            """,
            (template_type,),
        ).fetchall()

        templates = []
        for row in rows:
            templates.append(
                {
                    "id": row["id"],
                    "template_type": row["template_type"],
                    "template_name": row["template_name"],
                    "is_default": bool(row["is_default"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "created_by": row.get("created_by"),
                }
            )

        return jsonify({"success": True, "templates": templates})
    finally:
        conn.close()


@bp.route("/api/print-templates", methods=["POST"])
def save_template():
    """Save or update a print template."""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()
    template_type = data.get("template_type")
    template_name = data.get("template_name", "Default")
    layout = data.get("layout")
    is_default = data.get("is_default", False)

    if not template_type or not layout:
        return jsonify({"error": "template_type and layout are required"}), 400

    # Validate template_type
    valid_types = [
        "job_worksheet",
        "job_worksheet_production",
        "job_worksheet_railing",
        "intake_form",
        "railing_intake",
    ]
    if template_type not in valid_types:
        return (
            jsonify({"error": f"Invalid template_type. Must be one of: {', '.join(valid_types)}"}),
            400,
        )

    now = datetime.now().isoformat()
    username = get_current_username() or "admin"

    conn = connect()
    try:
        # If setting as default, unset other defaults for this type
        if is_default:
            conn.execute(
                "UPDATE print_templates SET is_default = 0 WHERE template_type = ?",
                (template_type,),
            )

        # Check if template already exists
        existing = conn.execute(
            "SELECT id FROM print_templates WHERE template_type = ? AND template_name = ?",
            (template_type, template_name),
        ).fetchone()

        if existing:
            # Update existing template
            conn.execute(
                """
                UPDATE print_templates
                SET layout_json = ?, is_default = ?, updated_at = ?
                WHERE id = ?
                """,
                (json.dumps(layout), int(is_default), now, existing["id"]),
            )
            template_id = existing["id"]
        else:
            # Insert new template
            result = conn.execute(
                """
                INSERT INTO print_templates (template_type, template_name, layout_json, is_default, created_at, updated_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """,
                (
                    template_type,
                    template_name,
                    json.dumps(layout),
                    int(is_default),
                    now,
                    now,
                    username,
                ),
            )
            row = result.fetchone()
            template_id = row["id"] if row else None

        conn.commit()

        return jsonify(
            {"success": True, "message": "Template saved successfully", "template_id": template_id}
        )
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@bp.route("/api/print-templates/<int:template_id>", methods=["DELETE"])
def delete_template(template_id):
    """Delete a print template."""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403

    conn = connect()
    try:
        conn.execute("DELETE FROM print_templates WHERE id = ?", (template_id,))
        conn.commit()

        return jsonify({"success": True, "message": "Template deleted successfully"})
    finally:
        conn.close()


@bp.route("/api/print-templates/<int:template_id>/set-default", methods=["POST"])
def set_default_template(template_id):
    """Set a template as the default for its type."""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403

    conn = connect()
    try:
        # Get the template type
        template = conn.execute(
            "SELECT template_type FROM print_templates WHERE id = ?",
            (template_id,),
        ).fetchone()

        if not template:
            return jsonify({"error": "Template not found"}), 404

        # Unset other defaults for this type
        conn.execute(
            "UPDATE print_templates SET is_default = 0 WHERE template_type = ?",
            (template["template_type"],),
        )

        # Set this one as default
        conn.execute(
            "UPDATE print_templates SET is_default = 1, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), template_id),
        )

        conn.commit()

        return jsonify({"success": True, "message": "Template set as default"})
    finally:
        conn.close()
