from __future__ import annotations

import csv
import json
import os
from datetime import datetime
from io import StringIO

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from ..core.config import UPLOADS_DIR
from ..core.db import connect, db_execute, db_query_all, db_query_one, get_db, get_ui_settings
from ..core.options import get_powder_options, get_work_order_options
from ..core.security import has_perm, is_admin, require_admin
from ..core.uploads import allowed_upload
from ..core.utils import fmt_ts, slugify, to_float

bp = Blueprint("powders", __name__)


def _coerce_bool(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"", "none", "null"}:
        return None
    if text in {"1", "true", "yes", "y", "t", "on"}:
        return True
    if text in {"0", "false", "no", "n", "f", "off"}:
        return False
    return None


def _coerce_int(value):
    if value is None:
        return None
    try:
        if isinstance(value, str) and value.strip() == "":
            return None
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _prepare_powder_from_csv(row: dict, markup_percentage: float) -> dict | None:
    cleaned = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
    if not any((cleaned.get(k) or "").strip() for k in cleaned):
        return None
    powder_color = (cleaned.get("powder_color") or "").strip()
    if not powder_color:
        return None

    def _s(name: str) -> str:
        return (cleaned.get(name) or "").strip()

    price_per_kg = to_float(cleaned.get("price_per_kg"))
    shipping_cost = to_float(cleaned.get("shipping_cost"))
    charge_per_lb = to_float(cleaned.get("charge_per_lb"))
    charge_per_kg = to_float(cleaned.get("charge_per_kg"))

    if price_per_kg is not None:
        base = price_per_kg + (shipping_cost or 0)
        if markup_percentage and markup_percentage > 0:
            charge_per_kg = base * (1 + markup_percentage / 100)
            charge_per_lb = charge_per_kg / 2.20462
    if charge_per_kg is None and charge_per_lb is not None:
        charge_per_kg = charge_per_lb * 2.20462
    elif charge_per_lb is None and charge_per_kg is not None:
        charge_per_lb = charge_per_kg / 2.20462

    metallic = _coerce_bool(cleaned.get("metallic"))
    needs_clear = _coerce_bool(cleaned.get("needs_clear"))

    return {
        "id": _coerce_int(cleaned.get("id")),
        "created_at": _s("created_at") or None,
        "powder_color": powder_color,
        "color_family": _s("color_family"),
        "manufacturer": _s("manufacturer"),
        "product_code": _s("product_code"),
        "gloss_level": _s("gloss_level"),
        "finish": _s("finish"),
        "metallic": None if metallic is None else int(metallic),
        "needs_clear": None if needs_clear is None else int(needs_clear),
        "int_ext": _s("int_ext"),
        "additional_code": _s("additional_code"),
        "msds_url": _s("msds_url"),
        "sds_url": _s("sds_url"),
        "web_link": _s("web_link"),
        "notes": _s("notes"),
        "cure_schedule": _s("cure_schedule"),
        "additional_info": _s("additional_info"),
        "aliases": _s("aliases"),
        "price_per_kg": price_per_kg,
        "charge_per_kg": charge_per_kg,
        "charge_per_lb": charge_per_lb,
        "weight_box_kg": to_float(cleaned.get("weight_box_kg")),
        "last_price_check": _s("last_price_check"),
        "in_stock": to_float(cleaned.get("in_stock")),
        "shipping_cost": shipping_cost,
        "picture_url": _s("picture_url"),
    }


@bp.route("/powders")
def powders_page():
    if not (is_admin() or has_perm("see_powders")):
        return redirect(url_for("auth.login", next=url_for("powders.powders_page")))
    rows = db_query_all("SELECT * FROM powders ORDER BY LOWER(powder_color) ASC")
    opts = get_powder_options()
    return render_template(
        "powders.html",
        rows=rows,
        is_admin=is_admin(),
        opt_families=opts.get("color_families", []),
        opt_manufacturers=opts.get("manufacturers", []),
        opt_gloss=opts.get("gloss_levels", []),
        opt_finishes=opts.get("finishes", []),
        opt_int_ext=opts.get("int_ext", []),
        total_powders=len(rows),
    )


@bp.route("/powders/<int:pow_id>/edit")
def powder_edit(pow_id: int):
    if not is_admin():
        return redirect(url_for("auth.login", next=url_for("powders.powder_edit", pow_id=pow_id)))
    row = db_query_one("SELECT * FROM powders WHERE id=?", (pow_id,))
    if not row:
        abort(404)
    if not isinstance(row, dict):
        row = dict(row)
    color = (row.get("powder_color") or "").strip()
    cur_id = row.get("id")
    prev_row = db_query_one(
        """
        SELECT id FROM powders
        WHERE (LOWER(powder_color) < LOWER(?))
           OR (LOWER(powder_color) = LOWER(?) AND id < ?)
        ORDER BY LOWER(powder_color) DESC, id DESC
        LIMIT 1
        """,
        (color, color, cur_id),
    )
    next_row = db_query_one(
        """
        SELECT id FROM powders
        WHERE (LOWER(powder_color) > LOWER(?))
           OR (LOWER(powder_color) = LOWER(?) AND id > ?)
        ORDER BY LOWER(powder_color) ASC, id ASC
        LIMIT 1
        """,
        (color, color, cur_id),
    )
    opts = get_powder_options()
    return render_template(
        "powder_edit.html",
        powder=row,
        r=row,
        previous_id=prev_row["id"] if prev_row else None,
        next_id=next_row["id"] if next_row else None,
        opts=opts,
        is_admin=is_admin(),
        opt_families=opts.get("color_families", []),
        opt_manufacturers=opts.get("manufacturers", []),
        opt_gloss=opts.get("gloss_levels", []),
        opt_finishes=opts.get("finishes", []),
        opt_int_ext=opts.get("int_ext", []),
        opt_markup_percentage=opts.get("markup_percentage", 0),
    )


@bp.route("/powders/new")
def powder_new():
    if not is_admin():
        return redirect(url_for("auth.login", next=url_for("powders.powder_new")))
    empty = {}
    opts = get_powder_options()
    return render_template(
        "powder_edit.html",
        powder=empty,
        r=empty,
        is_admin=is_admin(),
        opts=opts,
        previous_id=None,
        next_id=None,
        opt_families=opts.get("color_families", []),
        opt_manufacturers=opts.get("manufacturers", []),
        opt_gloss=opts.get("gloss_levels", []),
        opt_finishes=opts.get("finishes", []),
        opt_int_ext=opts.get("int_ext", []),
        opt_markup_percentage=opts.get("markup_percentage", 0),
    )


@bp.route("/powders/save", methods=["POST"])
def powders_save():
    guard = require_admin()
    if guard:
        return guard
    f = request.form
    pow_id = f.get("id")

    # Calculate charge values based on price and markup
    price_per_kg = to_float(f.get("price_per_kg"))
    shipping_cost = to_float(f.get("shipping_cost")) or 0
    opts = get_powder_options()
    markup_percentage = opts.get("markup_percentage", 0)

    charge_per_kg = None
    charge_per_lb = None
    if price_per_kg is not None and price_per_kg > 0 and markup_percentage > 0:
        # Include shipping cost in the base price, then apply markup
        base_price_with_shipping = price_per_kg + shipping_cost
        charge_per_kg = base_price_with_shipping * (1 + markup_percentage / 100)
        charge_per_lb = charge_per_kg / 2.20462  # Convert kg to lb

    fields = (
        f.get("powder_color", "").strip(),
        (f.get("color_family") or "").strip(),
        f.get("manufacturer", "").strip(),
        f.get("product_code", "").strip(),
        f.get("gloss_level", "").strip(),
        f.get("finish", "").strip(),
        1 if f.get("metallic") == "on" else 0,
        1 if f.get("needs_clear") == "on" else 0,
        f.get("int_ext", "").strip(),
        f.get("additional_code", "").strip(),
        f.get("msds_url", "").strip(),
        f.get("sds_url", "").strip(),
        f.get("web_link", "").strip(),
        f.get("notes", "").strip(),
        (f.get("cure_schedule") or "").strip(),
        (f.get("additional_info") or "").strip(),
        (f.get("aliases") or "").strip(),
        price_per_kg,
        charge_per_kg,
        charge_per_lb,
        to_float(f.get("weight_box_kg")),
        f.get("last_price_check", "").strip(),
        to_float(f.get("in_stock")),
        to_float(f.get("shipping_cost")),
        f.get("picture_url", "").strip(),
    )
    if not fields[0]:
        abort(400, "powder_color required")
    if pow_id:
        db_execute(
            """
            UPDATE powders SET
              powder_color=?, color_family=?, manufacturer=?, product_code=?, gloss_level=?, finish=?, metallic=?, needs_clear=?,
              int_ext=?, additional_code=?, msds_url=?, sds_url=?, web_link=?, notes=?, cure_schedule=?, additional_info=?, aliases=?, price_per_kg=?, charge_per_kg=?, charge_per_lb=?,
              weight_box_kg=?, last_price_check=?, in_stock=?, shipping_cost=?, picture_url=?
            WHERE id=?
            """,
            (*fields, pow_id),
        )
    else:
        db_execute(
            """
            INSERT INTO powders (
              created_at, powder_color, color_family, manufacturer, product_code, gloss_level, finish, metallic, needs_clear,
              int_ext, additional_code, msds_url, sds_url, web_link, notes, cure_schedule, additional_info, aliases, price_per_kg, charge_per_kg, charge_per_lb,
              weight_box_kg, last_price_check, in_stock, shipping_cost, picture_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), *fields),
        )
    flash("Powder updated." if pow_id else "Powder added.", "success")
    return redirect(url_for("powders.powders_page"))


@bp.route("/powders/<int:pow_id>/delete", methods=["POST"])
def powders_delete(pow_id: int):
    guard = require_admin()
    if guard:
        return guard
    db_execute("DELETE FROM powders WHERE id=?", (pow_id,))
    return redirect(url_for("powders.powders_page"))


def _powder_asset_dir(pow_id: int) -> str:
    row = db_query_one(
        "SELECT manufacturer, powder_color, product_code FROM powders WHERE id=?",
        (pow_id,),
    )
    manufacturer = (row and row.get("manufacturer")) or "unknown"
    color = (row and row.get("powder_color")) or "unknown"
    code = (row and row.get("product_code")) or ""
    manu_seg = slugify(manufacturer) or "unknown"
    color_code = f"{color} - {code}".strip(" -") if code else str(color)
    color_seg = slugify(color_code) or "color"
    return os.path.join(UPLOADS_DIR, "powders", manu_seg, color_seg)


@bp.route("/powders/<int:pow_id>/upload/<field>", methods=["POST"])
def powders_upload(pow_id: int, field: str):
    guard = require_admin()
    if guard:
        return guard
    field = (field or "").strip().lower()
    col_map = {"msds": "msds_url", "sds": "sds_url", "picture": "picture_url"}
    if field not in col_map:
        abort(400, description="Invalid upload field")

    file = request.files.get("file")
    if not file or not getattr(file, "filename", None):
        abort(400, description="No file provided")
    if not allowed_upload(file.filename):
        abort(400, description="Unsupported file type")

    try:
        subdir = _powder_asset_dir(pow_id)
        os.makedirs(subdir, exist_ok=True)
    except Exception:
        abort(500, description="Unable to create upload directory")

    base, ext = os.path.splitext(secure_filename(file.filename))
    safe_ext = ext.lower() or ""
    target_name = f"{field}{safe_ext}" if safe_ext else field
    abs_path = os.path.join(subdir, target_name)
    try:
        file.save(abs_path)
    except Exception:
        abort(500, description="Failed to save file")

    rel_path = os.path.relpath(abs_path, UPLOADS_DIR).replace("\\", "/")
    db_execute(
        f"UPDATE powders SET {col_map[field]}=? WHERE id=?",
        (rel_path, pow_id),
    )
    flash(f"{field.upper()} uploaded.", "success")
    return redirect(url_for("powders.powder_edit", pow_id=pow_id))


@bp.route("/powders.csv")
def powders_csv():
    ui = get_ui_settings()
    if not ui.get("show_csv", False):
        abort(404)
    if not (is_admin() or has_perm("see_csv")):
        return redirect(url_for("auth.login", next=request.path))

    rows = db_query_all("SELECT * FROM powders ORDER BY LOWER(powder_color) ASC")
    fieldnames = [
        "id",
        "created_at",
        "powder_color",
        "color_family",
        "manufacturer",
        "product_code",
        "gloss_level",
        "finish",
        "metallic",
        "needs_clear",
        "int_ext",
        "additional_code",
        "msds_url",
        "sds_url",
        "web_link",
        "notes",
        "cure_schedule",
        "additional_info",
        "aliases",
        "price_per_kg",
        "charge_per_lb",
        "weight_box_kg",
        "last_price_check",
        "in_stock",
        "shipping_cost",
        "picture_url",
    ]
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        record = dict(row)
        record["metallic"] = bool(record.get("metallic"))
        record["needs_clear"] = bool(record.get("needs_clear"))
        writer.writerow({k: record.get(k) for k in fieldnames})
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": 'attachment; filename="powders.csv"'},
    )


@bp.route("/powders/import", methods=["POST"])
def powders_import():
    guard = require_admin()
    if guard:
        return guard
    file = request.files.get("file")
    if not file or not getattr(file, "filename", None):
        flash("Please choose a CSV file to upload.", "error")
        return redirect(url_for("powders.powders_page"))

    filename = file.filename.lower()
    if not filename.endswith(".csv"):
        flash("Only CSV files are supported.", "error")
        return redirect(url_for("powders.powders_page"))

    try:
        raw = file.read()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
    except Exception:
        flash("Unable to read uploaded file.", "error")
        return redirect(url_for("powders.powders_page"))

    stream = StringIO(text)
    try:
        reader = csv.DictReader(stream)
    except Exception:
        flash("Invalid CSV format.", "error")
        return redirect(url_for("powders.powders_page"))

    if not reader.fieldnames or "powder_color" not in [
        h.strip().lower() for h in reader.fieldnames if h
    ]:
        flash("CSV must include a 'powder_color' column.", "error")
        return redirect(url_for("powders.powders_page"))

    opts = get_powder_options()
    markup = to_float(opts.get("markup_percentage")) or 0

    conn = connect()
    processed = inserted = updated = skipped = 0
    columns = [
        "powder_color",
        "color_family",
        "manufacturer",
        "product_code",
        "gloss_level",
        "finish",
        "metallic",
        "needs_clear",
        "int_ext",
        "additional_code",
        "msds_url",
        "sds_url",
        "web_link",
        "notes",
        "cure_schedule",
        "additional_info",
        "aliases",
        "price_per_kg",
        "charge_per_kg",
        "charge_per_lb",
        "weight_box_kg",
        "last_price_check",
        "in_stock",
        "shipping_cost",
        "picture_url",
    ]

    try:
        for row in reader:
            processed += 1
            normalized = _prepare_powder_from_csv(row, markup)
            if not normalized:
                skipped += 1
                continue

            powder_id = normalized.pop("id", None)
            created_at = normalized.pop("created_at", None)

            params = [normalized.get(col) for col in columns]

            if powder_id:
                existing = conn.execute(
                    "SELECT id FROM powders WHERE id=?", (powder_id,)
                ).fetchone()
                if existing:
                    set_clause = ", ".join(f"{col}=?" for col in columns)
                    conn.execute(
                        f"UPDATE powders SET {set_clause} WHERE id=?",
                        (*params, powder_id),
                    )
                    updated += 1
                    continue

            insert_cols = ["created_at", *columns]
            insert_values = [created_at or datetime.now().isoformat(), *params]
            conn.execute(
                f"INSERT INTO powders ({', '.join(insert_cols)}) VALUES ({', '.join(['?'] * len(insert_cols))})",
                insert_values,
            )
            inserted += 1

        conn.commit()
    except Exception as exc:
        conn.close()
        flash(f"CSV import failed: {exc}", "error")
        return redirect(url_for("powders.powders_page"))

    conn.close()

    message = f"Processed {processed} rows: {updated} updated, {inserted} added"
    if skipped:
        message += f", {skipped} skipped"
    flash(message + ".", "success")
    return redirect(url_for("powders.powders_page"))


@bp.route("/powders/families.json")
def powders_families():
    rows = db_query_all(
        """
        SELECT DISTINCT color_family AS fam
          FROM powders
         WHERE color_family IS NOT NULL AND TRIM(color_family) <> ''
         ORDER BY fam ASC
        """
    )
    return jsonify([r["fam"] for r in rows])


@bp.route("/powders/colors_full.json")
def powders_colors_full():
    rows = db_query_all(
        """
        SELECT powder_color AS color, color_family AS family, aliases
          FROM powders
         ORDER BY LOWER(powder_color) ASC
        """
    )
    data = []
    for r in rows:
        aliases = [alias.strip() for alias in (r.get("aliases") or "").split(",") if alias.strip()]
        data.append(
            {
                "color": r["color"],
                "family": r["family"],
                "aliases": aliases,
            }
        )
    return jsonify(data)


@bp.route("/powders/by_color.json")
def powders_by_color():
    name = (request.args.get("name") or "").strip()
    if not name:
        return jsonify({}), 400
    row = db_query_one(
        """
        SELECT
            id,
            powder_color AS color,
            color_family AS family,
            manufacturer,
            product_code,
            gloss_level,
            finish,
            metallic,
            needs_clear,
            int_ext,
            in_stock,
            aliases,
            notes,
            additional_info,
            cure_schedule
          FROM powders
         WHERE lower(trim(powder_color)) = lower(trim(?))
         LIMIT 1
        """,
        (name,),
    )
    if not row:
        alt = db_query_one(
            """
            SELECT
                id,
                powder_color AS color,
                color_family AS family,
                manufacturer,
                product_code,
                gloss_level,
                finish,
                metallic,
                needs_clear,
                int_ext,
                in_stock,
                aliases,
                notes,
                additional_info,
                cure_schedule
              FROM powders
             WHERE aliases IS NOT NULL
               AND aliases <> ''
               AND lower(aliases) LIKE lower(?)
             ORDER BY LENGTH(aliases) ASC
             LIMIT 1
            """,
            (f"%{name}%",),
        )
        row = alt
    if not row:
        return jsonify({}), 404
    if not isinstance(row, dict):
        row = dict(row)

    def _clean(val):
        if val is None:
            return None
        if isinstance(val, str):
            return val.strip() or None
        return val

    def _as_bool(val):
        if val is None:
            return False
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return bool(val)
        s = str(val).strip().lower()
        return s in ("1", "true", "yes", "y", "on")

    data = {
        "id": row.get("id"),
        "color": _clean(row.get("color")),
        "family": _clean(row.get("family")),
        "manufacturer": _clean(row.get("manufacturer")),
        "product_code": _clean(row.get("product_code")),
        "gloss_level": _clean(row.get("gloss_level")),
        "finish": _clean(row.get("finish")),
        "metallic": _as_bool(row.get("metallic")),
        "needs_clear": _as_bool(row.get("needs_clear")),
        "int_ext": _clean(row.get("int_ext")),
        "in_stock": row.get("in_stock"),
        "aliases": _clean(row.get("aliases")),
        "notes": _clean(row.get("notes")),
        "cure_schedule": _clean(row.get("cure_schedule")),
        "additional_info": _clean(row.get("additional_info")),
    }
    return jsonify(data)


@bp.get("/powders/<int:pow_id>.json")
def powder_detail_json(pow_id: int):
    db = get_db()
    row = db.execute(
        """
        SELECT id, powder_color, manufacturer, product_code, gloss_level, finish,
               metallic, needs_clear, int_ext, additional_code,
               on_hand_kg, last_weighed_kg, last_weighed_at,
               in_stock, weight_box_kg,
               picture_url, msds_url, sds_url, web_link, notes, additional_info, cure_schedule
          FROM powders WHERE id=?
        """,
        (pow_id,),
    ).fetchone()
    if not row:
        return jsonify({}), 404
    record = dict(row)
    return jsonify(
        {
            "id": record["id"],
            "powder_color": record["powder_color"],
            "manufacturer": record["manufacturer"],
            "product_code": record["product_code"],
            "gloss_level": record["gloss_level"],
            "finish": record["finish"],
            "metallic": record["metallic"],
            "needs_clear": record["needs_clear"],
            "int_ext": record["int_ext"],
            "additional_code": record["additional_code"],
            "on_hand_kg": record["on_hand_kg"],
            "last_weighed_kg": record["last_weighed_kg"],
            "last_weighed_at": record["last_weighed_at"],
            "in_stock": record["in_stock"],
            "weight_box_kg": record["weight_box_kg"],
            "picture_url": record["picture_url"],
            "msds_url": record["msds_url"],
            "sds_url": record["sds_url"],
            "web_link": record["web_link"],
            "notes": record["notes"],
            "additional_info": record["additional_info"],
            "cure_schedule": record.get("cure_schedule"),
        }
    )
