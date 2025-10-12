PowderApp 1.2

Overview
- Flask app backed by Postgres for job intake, jobs board, customers, and powder inventory.
- Layout:
  - App factory: `src/powder_app/__init__.py`
  - CLI entry: `src/powder_app/main.py`
  - Blueprints: `src/powder_app/blueprints/`
  - Core helpers: `src/powder_app/core/`
  - Templates: `src/powder_app/templates/`
  - Static assets: `src/powder_app/static/`
  - Runtime data: `storage/data/` (uploads, exports, backups)
  - Tools: `tools/` (backup, import, rebuild, restore, migration)

Environment
- `.env` example (Postgres required):

  ADMIN_PIN=1234
  SECRET_KEY=change_me_for_prod
  FLASK_DEBUG=0
  TZ=America/Vancouver
  DB_BACKEND=postgres
  PGHOST=192.168.0.207
  PGPORT=5432
  PGDATABASE=powderapp
  PGUSER=Harley
  PGPASSWORD=super_secret

Quick Start (Docker, no Compose)
1) Build the image:

   docker build -t powderapp:1.2 .

2) Run the container (bind uploads to persistent storage):

   docker run -d --name PowderApp1.2 \
     --restart unless-stopped \
     -p 5001:5000 \
     --env-file .env \
     -v /mnt/user/appdata/PowderApp1.2/storage/data:/app/storage/data \
     powderapp:1.2

   Or with a named volume:

   docker volume create powderapp1_storage
   docker run -d --name PowderApp1.2 \
     --restart unless-stopped \
     -p 5001:5000 \
     --env-file .env \
     -v powderapp1_storage:/app/storage/data \
     powderapp:1.2

3) Open the app:
- Nav: http://<UNRAID-IP>:5001/nav
- Admin: http://<UNRAID-IP>:5001/login (PIN is ADMIN_PIN)

Data Persistence
- `storage/data/uploads/` holds photos and other user files (bind-mount it on Unraid).
- Application state lives in Postgres; confirm connectivity with `docker exec -it PowderApp1.2 env | grep PG`.

Updating
- Rebuild + restart while keeping the uploads mount and Postgres connection:

  docker build -t powderapp:1.2 . && \
  docker stop PowderApp1.2 && docker rm PowderApp1.2 && \
  docker run -d --name PowderApp1.2 \
    --restart unless-stopped \
    -p 5001:5000 \
    --env-file .env \
    -v /mnt/user/appdata/PowderApp1.2/storage/data:/app/storage/data \
    powderapp:1.2

Tools
- Rebuild helper: `tools/rebuild.sh`
  - Mounts the repo read-only and keeps uploads under `/app/storage/data`.
  - Override the host path with `DATA_DIR=/mnt/user/appdata/PowderApp1.2/storage/data` if needed.
- Backups:
  - PowerShell: `powershell -ExecutionPolicy Bypass -File tools\backup.ps1 -IncludeDb -IncludeUploads`
  - Bash: `INCLUDE_DB=1 INCLUDE_UPLOADS=1 bash tools/backup.sh`
  - Both scripts dump Postgres (via `pg_dump`) and optionally archive uploads.
- Restore DB (Bash): `bash tools/restore_db.sh <pgdump.dump|backup.zip> [--include-uploads]`
- Restore DB (PowerShell): `powershell -ExecutionPolicy Bypass -File tools\restore.ps1 <pgdump.dump|backup.zip> [-IncludeUploads]`
- Imports: `python tools/import_powders_csv.py path/to/powders.csv [--update-existing]`

Live Edits (no rebuild)
- For auto-reloading Python/templates/static while pointing at Postgres:

  docker run -d --name PowderApp1.2 \
    --restart unless-stopped \
    -p 5001:5000 \
    --env-file .env -e GUNICORN_RELOAD=1 \
    -v /mnt/user/appdata/PowderApp1.2:/app:ro \
    -v /mnt/user/appdata/PowderApp1.2/storage/data:/app/storage/data \
    powderapp:1.2

Unraid UI (no CLI)
1) Docker tab -> Add Container
2) Name: PowderApp1.2
3) Repository: powderapp:1.2 (after you build locally)
4) Add Port: Host 5001 -> Container 5000
5) Add Path: Host `/mnt/user/appdata/PowderApp1.2/storage/data` -> Container `/app/storage/data`
6) Add variables: ADMIN_PIN, SECRET_KEY, TZ, DB_BACKEND=postgres, PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD, optional FLASK_DEBUG/GUNICORN_WORKERS
7) Apply -> Start

Local Development (without Docker)
- Requirements: Python 3.11, Postgres connection available.
- Setup:

  python -m venv .venv
  . .venv/bin/activate    # Windows: .venv\Scripts\activate
  pip install -r requirements.txt

- Run (ensure PG* env vars are set):

  python -m flask --app powder_app.main run

- Open: http://127.0.0.1:5000/nav

Notes
- `.dockerignore` excludes uploads/backups to keep the build context small.
- CSV exports are managed via the Admin panel.

Local Postgres (Docker Compose)
- Ensure Docker is running, then from the project root:

  mkdir -p storage/pgdata
  docker compose -f docker-compose.postgres.yml up -d

- Create a `.env` file (ignored by git) with:

  DB_BACKEND=postgres
  PGHOST=127.0.0.1
  PGPORT=5432
  PGDATABASE=PowderAppDB
  PGUSER=Harley
  PGPASSWORD=Chaotic

- Restart the app to pick up the new connection settings. Stop the database with:

  docker compose -f docker-compose.postgres.yml down

Postgres Setup & Legacy Migration
- Create the Postgres database manually (if not using Docker Compose):

  CREATE DATABASE PowderAppDB;
  CREATE USER "Harley" WITH PASSWORD 'Chaotic';
  GRANT ALL PRIVILEGES ON DATABASE "PowderAppDB" TO "Harley";

- To migrate from an existing Postgres server:

  # On the Unraid server (replace host/port/db/user as needed)
  PGPASSWORD=Chaotic pg_dump -h 127.0.0.1 -p 5432 -U Harley PowderAppDB -Fc -f /tmp/powderapp.dump

  # Copy the dump to this project folder (example)
  scp user@unraid:/tmp/powderapp.dump ./

  # Restore into the local Docker Postgres
  docker compose -f docker-compose.postgres.yml exec -T postgres pg_restore -U Harley -d PowderAppDB --clean --if-exists < powderapp.dump

- Alternatively, place the dump in the project root and run:

  PGHOST=127.0.0.1 PGPORT=5432 PGDATABASE=PowderAppDB PGUSER=Harley PGPASSWORD=Chaotic \
    bash tools/restore_db.sh powderapp.dump

- To migrate an old SQLite `app.db`, stop the app and run:

  python tools/migrate_sqlite_to_postgres.py \
    --host 192.168.0.207 --port 5432 --db powderapp \
    --user Harley --password 'super_secret' \
    --sqlite storage/data/app.db

- After migration, remove any leftover `storage/data/app.db` so the app cannot fall back to SQLite.

Uploads/Photos
- User uploads remain under `storage/data/uploads/` for easy SMB access on Unraid; back them up alongside your Postgres dumps.
