import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
os.environ.setdefault('DB_BACKEND', 'postgres')
os.environ.setdefault('STORAGE_DIR', str(root / 'storage'))
sys.path.insert(0, str(root / 'src'))

from powder_app import create_app

app = create_app()
client = app.test_client()
with client.session_transaction() as sess:
    sess['is_admin'] = True

pages = [
    ('/sprayer/batches', 'sprayer_batches.html'),
    ('/sprayer/hitlist', 'sprayer_hitlist.html'),
]

out_dir = root / 'storage' / 'tmp'
out_dir.mkdir(parents=True, exist_ok=True)

for endpoint, filename in pages:
    resp = client.get(endpoint)
    if resp.status_code != 200:
        print(f"{endpoint} -> {resp.status_code}")
        continue
    path = out_dir / filename
    path.write_text(resp.get_data(as_text=True), encoding='utf-8')
    print(f"wrote {path}")
