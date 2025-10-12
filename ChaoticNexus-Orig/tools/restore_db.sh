#!/usr/bin/env bash
set -euo pipefail

# Restore the application database from a provided source.
# Supports:
#  - Postgres pg_dump (.dump) or .sql backups
#  - zip/dir containing uploads and PG dumps
#  - Legacy SQLite app.db will be migrated into Postgres during restore
# Usage:
#   bash tools/restore_db.sh <path|zip> [--include-uploads]
# Env overrides:
#   CONTAINER=PowderApp1.2
#   DATA_DIR=/mnt/user/appdata/PowderApp1.2/storage/data
#   PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD for Postgres

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONTAINER="${CONTAINER:-PowderApp1.2}"
DATA_DIR="${DATA_DIR:-$APP_DIR/storage/data}"
INCLUDE_UPLOADS=0

usage() {
  echo "Usage: $0 <app.db|backup_dir|backup.zip|pg_dump.dump|db.sql> [--include-uploads]" >&2
  exit 1
}

[ $# -ge 1 ] || usage
SRC="$1"; shift || true
while [ $# -gt 0 ]; do
  case "$1" in
    --include-uploads) INCLUDE_UPLOADS=1 ;;
    -h|--help) usage ;;
    *) echo "Unknown arg: $1" >&2; usage ;;
  esac
  shift || true
done

echo "==> Data directory: $DATA_DIR"
mkdir -p "$DATA_DIR"

# Detect backend from env/.env
BACKEND="${DB_BACKEND:-}"
if [[ -z "$BACKEND" && -f "$APP_DIR/.env" ]]; then
  BACKEND=$(grep -E '^DB_BACKEND=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r' | tr '[:upper:]' '[:lower:]')
fi
BACKEND="${BACKEND:-postgres}"
if [[ "$BACKEND" != "postgres" ]]; then
  echo "ERROR: PowderApp now requires Postgres. Set DB_BACKEND=postgres." >&2
  exit 2
fi

# Stop app container (best effort)
if command -v docker >/dev/null 2>&1; then
  CID="$(docker ps -q -f name="^${CONTAINER}$" || true)"
  if [ -n "$CID" ]; then
    echo "==> Stopping container: $CONTAINER"
    docker stop "$CONTAINER" >/dev/null || true
  fi
fi

TS="$(date +%Y-%m-%d_%H-%M-%S)"

restore_postgres_dump() {
  local DUMP_FILE="$1"
  # Read PG connection from env or .env
  local PGHOST_="${PGHOST:-}"; local PGPORT_="${PGPORT:-}"; local PGDATABASE_="${PGDATABASE:-}"; local PGUSER_="${PGUSER:-}"; local PGPASSWORD_="${PGPASSWORD:-}"
  if [[ -z "$PGHOST_" && -f "$APP_DIR/.env" ]]; then PGHOST_=$(grep -E '^PGHOST=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGPORT_" && -f "$APP_DIR/.env" ]]; then PGPORT_=$(grep -E '^PGPORT=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGDATABASE_" && -f "$APP_DIR/.env" ]]; then PGDATABASE_=$(grep -E '^PGDATABASE=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGUSER_" && -f "$APP_DIR/.env" ]]; then PGUSER_=$(grep -E '^PGUSER=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGPASSWORD_" && -f "$APP_DIR/.env" ]]; then PGPASSWORD_=$(grep -E '^PGPASSWORD=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  : "${PGHOST_:?PGHOST not set}"; : "${PGPORT_:?PGPORT not set}"; : "${PGDATABASE_:?PGDATABASE not set}"; : "${PGUSER_:?PGUSER not set}"; : "${PGPASSWORD_:?PGPASSWORD not set}"
  echo "==> Restoring Postgres from dump: $DUMP_FILE"
  docker run --rm -e PGPASSWORD="$PGPASSWORD_" -v "$(dirname "$DUMP_FILE"):/backup" postgres:17 \
    pg_restore -h "$PGHOST_" -p "${PGPORT_:-5432}" -U "$PGUSER_" -d "$PGDATABASE_" --clean --if-exists --no-owner "/backup/$(basename "$DUMP_FILE")"
}

restore_postgres_sql() {
  local SQL_FILE="$1"
  local PGHOST_="${PGHOST:-}"; local PGPORT_="${PGPORT:-}"; local PGDATABASE_="${PGDATABASE:-}"; local PGUSER_="${PGUSER:-}"; local PGPASSWORD_="${PGPASSWORD:-}"
  if [[ -z "$PGHOST_" && -f "$APP_DIR/.env" ]]; then PGHOST_=$(grep -E '^PGHOST=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGPORT_" && -f "$APP_DIR/.env" ]]; then PGPORT_=$(grep -E '^PGPORT=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGDATABASE_" && -f "$APP_DIR/.env" ]]; then PGDATABASE_=$(grep -E '^PGDATABASE=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGUSER_" && -f "$APP_DIR/.env" ]]; then PGUSER_=$(grep -E '^PGUSER=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGPASSWORD_" && -f "$APP_DIR/.env" ]]; then PGPASSWORD_=$(grep -E '^PGPASSWORD=' "$APP_DIR/.env" | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  : "${PGHOST_:?PGHOST not set}"; : "${PGPORT_:?PGPORT not set}"; : "${PGDATABASE_:?PGDATABASE not set}"; : "${PGUSER_:?PGUSER not set}"; : "${PGPASSWORD_:?PGPASSWORD not set}"
  echo "==> Restoring Postgres from SQL: $SQL_FILE"
  docker run --rm -e PGPASSWORD="$PGPASSWORD_" -v "$(dirname "$SQL_FILE"):/backup" postgres:17 \
    psql -h "$PGHOST_" -p "${PGPORT_:-5432}" -U "$PGUSER_" -d "$PGDATABASE_" -f "/backup/$(basename "$SQL_FILE")"
}

# Unpack zip to temp if needed
TMP_DIR=""
SRC_PATH=""
if [ -f "$SRC" ] && [[ "$SRC" == *.zip ]]; then
  command -v unzip >/dev/null 2>&1 || { echo "ERROR: unzip not found; cannot read from zip" >&2; exit 3; }
  TMP_DIR="$(mktemp -d)"; trap 'rm -rf "$TMP_DIR"' EXIT
  echo "==> Extracting zip to temp: $TMP_DIR"
  unzip -oq "$SRC" -d "$TMP_DIR"
  SRC_PATH="$TMP_DIR"
elif [ -d "$SRC" ]; then
  SRC_PATH="$SRC"
else
  SRC_PATH="$(dirname "$SRC")"
fi

case "$BACKEND" in
  postgres)
    if [ -f "$SRC" ] && [[ "$SRC" == *.dump ]]; then
      restore_postgres_dump "$SRC"
    elif [ -f "$SRC" ] && [[ "$SRC" == *.sql ]]; then
      restore_postgres_sql "$SRC"
    elif [ -n "$SRC_PATH" ]; then
      # Look for .dump inside path
      DUMP_CAND="$(find "$SRC_PATH" -maxdepth 2 -type f -name '*.dump' | head -n1 || true)"
      if [ -n "$DUMP_CAND" ]; then
        restore_postgres_dump "$DUMP_CAND"
      elif [ -f "$SRC_PATH/app.db" ]; then
        echo "==> Migrating from SQLite app.db into Postgres"
        docker run --rm -it -e PGPASSWORD="${PGPASSWORD:-}" -v "$APP_DIR:/app" -w /app python:3.11-slim bash -lc \
          "pip install --no-cache-dir psycopg[binary]==3.2.1 >/dev/null && python tools/migrate_sqlite_to_postgres.py --host '${PGHOST:-}' --port '${PGPORT:-5432}' --db '${PGDATABASE:-}' --user '${PGUSER:-}' --sqlite '$SRC_PATH/app.db'"
      else
        echo "ERROR: Could not find .dump or app.db in: $SRC" >&2; exit 7
      fi
    fi
    ;;
  *)
    echo "ERROR: PowderApp now requires Postgres. Set DB_BACKEND=postgres." >&2; exit 8
    ;;
esac

# Restart container (best effort)
if command -v docker >/dev/null 2>&1; then
  echo "==> Starting container: $CONTAINER"
  docker start "$CONTAINER" >/dev/null || true
fi

echo "==> Restore complete. Verify via /admin/dbinfo in the app."
