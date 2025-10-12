import sqlite3, os

def main():
    db = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage', 'data', 'app.db')
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cols = [r[1] for r in cur.execute('PRAGMA table_info(powders)').fetchall()]
    changed = False
    if 'color_family' not in cols:
        cur.execute('ALTER TABLE powders ADD COLUMN color_family TEXT')
        changed = True
    if 'aliases' not in cols:
        cur.execute('ALTER TABLE powders ADD COLUMN aliases TEXT')
        changed = True
    if changed:
        conn.commit()
    print({'changed': changed, 'columns': [r[1] for r in cur.execute('PRAGMA table_info(powders)').fetchall()]})

if __name__ == '__main__':
    main()
