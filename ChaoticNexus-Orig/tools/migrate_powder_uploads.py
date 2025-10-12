import os
import sqlite3
import shutil


def slug(value: str) -> str:
    s = (value or '').strip().lower()
    out = []
    prev_dash = False
    for ch in s:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        else:
            if not prev_dash:
                out.append('-')
                prev_dash = True
    return ''.join(out).strip('-') or 'unknown'


def main():
    import sys
    dry_run = ('--dry-run' in sys.argv)
    root = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(root, 'storage', 'data')
    uploads_dir = os.path.join(data_dir, 'uploads')
    db_path = os.path.join(data_dir, 'app.db')

    os.makedirs(uploads_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT id, manufacturer, powder_color, product_code, picture_url, msds_url, sds_url FROM powders"
    ).fetchall()

    updated = 0
    moved_files = 0
    for r in rows:
        pid = r['id']
        manu_seg = slug(r['manufacturer'] or 'unknown')
        color_code = f"{r['powder_color'] or 'unknown'} - {r['product_code'] or ''}".strip(' -')
        color_seg = slug(color_code or 'color')
        target_dir = os.path.join(uploads_dir, 'powders', manu_seg, color_seg)
        if dry_run:
            # Skip creation in dry-run
            pass
        else:
            os.makedirs(target_dir, exist_ok=True)

        def move_rel(rel: str | None) -> str | None:
            nonlocal moved_files
            if not rel:
                return None
            src_abs = os.path.join(uploads_dir, rel)
            if not os.path.exists(src_abs):
                # Already moved or missing; try to detect if already in target
                dst_guess = os.path.join(target_dir, os.path.basename(rel))
                if os.path.exists(dst_guess):
                    return os.path.relpath(dst_guess, uploads_dir).replace('\\', '/')
                return rel
            dst_abs = os.path.join(target_dir, os.path.basename(rel))
            # If same path, nothing to do
            if os.path.abspath(src_abs) == os.path.abspath(dst_abs):
                return rel
            if dry_run:
                # Report planned move
                print({'move': rel, 'to': os.path.relpath(dst_abs, uploads_dir).replace('\\', '/')})
            else:
                os.makedirs(os.path.dirname(dst_abs), exist_ok=True)
                shutil.move(src_abs, dst_abs)
                moved_files += 1
            return os.path.relpath(dst_abs, uploads_dir).replace('\\', '/')

        pic_new = move_rel(r['picture_url'])
        msds_new = move_rel(r['msds_url'])
        sds_new = move_rel(r['sds_url'])

        if not dry_run:
            if pic_new != r['picture_url'] or msds_new != r['msds_url'] or sds_new != r['sds_url']:
                cur.execute(
                    "UPDATE powders SET picture_url=?, msds_url=?, sds_url=? WHERE id=?",
                    (pic_new, msds_new, sds_new, pid)
                )
                updated += 1

    if not dry_run:
        conn.commit()
    conn.close()
    print({
        'updated_rows': updated,
        'moved_files': moved_files,
        'uploads_dir': uploads_dir,
    })


if __name__ == '__main__':
    main()
