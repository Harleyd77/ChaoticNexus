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
    return ''.join(out).strip('-') or 'walk-ins'


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(root, 'storage', 'data')
    uploads_dir = os.path.join(data_dir, 'uploads')
    db_path = os.path.join(data_dir, 'app.db')

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT jp.id as pid, jp.job_id, jp.filename, jp.original_name, j.company "
        "FROM job_photos jp JOIN jobs j ON j.id = jp.job_id"
    ).fetchall()

    dry_run = ('--dry-run' in os.sys.argv)
    moved = 0
    updated = 0

    for r in rows:
        fname = r['filename']
        # If already nested (has a path separator), assume migrated
        if '/' in fname or '\\' in fname:
            continue
        company_seg = slug(r['company'] or '')
        target_dir = os.path.join(uploads_dir, 'jobs', company_seg, f"job-{r['job_id']}")
        src_abs = os.path.join(uploads_dir, fname)
        if not os.path.exists(src_abs):
            continue
        dst_abs = os.path.join(target_dir, os.path.basename(fname))
        rel_new = os.path.relpath(dst_abs, uploads_dir).replace('\\', '/')
        if dry_run:
            print({'move': fname, 'to': rel_new})
        else:
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(src_abs, dst_abs)
            moved += 1
            cur.execute("UPDATE job_photos SET filename=? WHERE id=?", (rel_new, r['pid']))
            updated += 1

    if not dry_run:
        conn.commit()
    conn.close()
    print({'moved_files': moved, 'updated_rows': updated, 'uploads_dir': uploads_dir})


if __name__ == '__main__':
    main()

