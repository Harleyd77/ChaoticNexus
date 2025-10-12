#!/usr/bin/env python3
"""
Import powders from a CSV (exported from Excel) into the app's SQLite DB.

Usage:
  python scripts/import_powders_csv.py path/to/powders.csv [--update-existing]

CSV header mapping is case-insensitive. Recommended headers:
  powder_color, manufacturer, product_code, gloss_level, finish, metallic, needs_clear,
  int_ext, additional_code, msds_url, sds_url, web_link, notes,
  price_per_kg, charge_per_lb, weight_box_kg, last_price_check, in_stock, shipping_cost, picture_url

Only powder_color is required. created_at is set automatically.

Tip: In Excel, Save As -> CSV (UTF-8). Then run this script.
"""

from __future__ import annotations
import sys, csv, os
from datetime import datetime

try:
    # Reuse the app's DB connection + schema
    from pathlib import Path as _P
    _ROOT = _P(__file__).resolve().parents[1]
    _SRC = _ROOT / 'src'
    if str(_SRC) not in sys.path:
        sys.path.insert(0, str(_SRC))
    from powder_app import main as vpc_app
except Exception as e:
    print("Error: could not import powder_app.main (ensure you run from repo root):", e, file=sys.stderr)
    sys.exit(1)


def norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "_")


FIELD_MAP = {
    # CSV header -> DB column name (both normalized)
    "powder_color": "powder_color",
    "color": "powder_color",
    "manufacturer": "manufacturer",
    "product_code": "product_code",
    "code": "product_code",
    "gloss_level": "gloss_level",
    "gloss": "gloss_level",
    "finish": "finish",
    "metallic": "metallic",
    "needs_clear": "needs_clear",
    "int_ext": "int_ext",
    "interior_exterior": "int_ext",
    "additional_code": "additional_code",
    "msds_url": "msds_url",
    "sds_url": "sds_url",
    "web_link": "web_link",
    "url": "web_link",
    "notes": "notes",
    "price_per_kg": "price_per_kg",
    "price/kg": "price_per_kg",
    "charge_per_lb": "charge_per_lb",
    "charge/lb": "charge_per_lb",
    "weight_box_kg": "weight_box_kg",
    "box_weight_kg": "weight_box_kg",
    "last_price_check": "last_price_check",
    "in_stock": "in_stock",
    "stock": "in_stock",
    "shipping_cost": "shipping_cost",
    "picture_url": "picture_url",
    "image_url": "picture_url",
}


BOOL_TRUES = {"1", "true", "yes", "y", "t"}


def to_bool(v) -> int | None:
    if v is None:
        return None
    s = str(v).strip().lower()
    if s == "":
        return None
    return 1 if s in BOOL_TRUES else 0


def to_float(v):
    try:
        sv = str(v).strip()
        if sv == "":
            return None
        return float(sv)
    except Exception:
        return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    csv_path = sys.argv[1]
    update_existing = "--update-existing" in sys.argv[2:]

    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Ensure DB/tables exist
    vpc_app.init_db()
    conn = vpc_app.connect()
    cur = conn.cursor()

    inserted = 0
    updated = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = [norm(h) for h in reader.fieldnames or []]

        # Build per-row mapping function
        key_map = {}
        for h in headers:
            db_col = FIELD_MAP.get(h)
            if db_col:
                key_map[h] = db_col

        if "powder_color" not in key_map.values():
            print("CSV must include a 'powder_color' column (or 'color').", file=sys.stderr)
            sys.exit(1)

        for raw in reader:
            row = {}
            for h_raw, value in raw.items():
                h = norm(h_raw)
                db_col = key_map.get(h)
                if not db_col:
                    continue
                row[db_col] = value

            # Coerce types
            row.setdefault("powder_color", (row.get("powder_color") or "").strip())
            if not row["powder_color"]:
                continue  # skip empty

            for b in ("metallic", "needs_clear"):
                if b in row:
                    row[b] = to_bool(row[b])

            for k in ("price_per_kg", "charge_per_lb", "weight_box_kg", "in_stock", "shipping_cost"):
                if k in row:
                    row[k] = to_float(row[k])

            # last_price_check: keep as text if provided

            if update_existing:
                # Update by matching powder_color + optional product_code if provided
                where = ["powder_color = ?"]
                params = [row["powder_color"]]
                if row.get("product_code"):
                    where.append("product_code = ?")
                    params.append(row["product_code"])

                existing = cur.execute(
                    f"SELECT id FROM powders WHERE {' AND '.join(where)} LIMIT 1",
                    params,
                ).fetchone()
                if existing:
                    sets = []
                    set_vals = []
                    for k, v in row.items():
                        if k in ("powder_color", "product_code"):
                            continue
                        sets.append(f"{k} = ?")
                        set_vals.append(v)
                    if sets:
                        cur.execute(
                            f"UPDATE powders SET {', '.join(sets)} WHERE id = ?",
                            (*set_vals, existing[0]),
                        )
                        updated += 1
                        continue

            # Insert new row
            cols = [
                "created_at", "powder_color", "manufacturer", "product_code", "gloss_level", "finish",
                "metallic", "needs_clear", "int_ext", "additional_code", "msds_url", "sds_url", "web_link",
                "notes", "price_per_kg", "charge_per_lb", "weight_box_kg", "last_price_check", "in_stock",
                "shipping_cost", "picture_url",
            ]
            values = [
                datetime.now().isoformat(),
                row.get("powder_color"), row.get("manufacturer"), row.get("product_code"), row.get("gloss_level"), row.get("finish"),
                row.get("metallic"), row.get("needs_clear"), row.get("int_ext"), row.get("additional_code"), row.get("msds_url"), row.get("sds_url"), row.get("web_link"),
                row.get("notes"), row.get("price_per_kg"), row.get("charge_per_lb"), row.get("weight_box_kg"), row.get("last_price_check"), row.get("in_stock"),
                row.get("shipping_cost"), row.get("picture_url"),
            ]
            cur.execute(
                """
                INSERT INTO powders (
                  created_at, powder_color, manufacturer, product_code, gloss_level, finish, metallic, needs_clear,
                  int_ext, additional_code, msds_url, sds_url, web_link, notes, price_per_kg, charge_per_lb,
                  weight_box_kg, last_price_check, in_stock, shipping_cost, picture_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            inserted += 1

    conn.commit()
    conn.close()
    print(f"Done. Inserted: {inserted}, Updated: {updated}")


if __name__ == "__main__":
    main()
