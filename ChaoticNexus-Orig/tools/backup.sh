#!/usr/bin/env bash
set -euo pipefail

# Project root = parent of this script's folder
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OUT_DIR="storage/backups/app"
mkdir -p "$OUT_DIR"
TS="$(date +%Y-%m-%d_%H-%M-%S)"
CODE_ARCHIVE=""

# Exclusions (defaults: skip secrets and large local data)
EXCLUDES=(
  --exclude='.venv'
  --exclude='.git'
  --exclude='node_modules'
  --exclude='__pycache__'
  --exclude='storage/backups'
  --exclude='storage/pgdata'
  --exclude='storage/pgdata/**'
  --exclude='.env'
  --exclude='backup'
  --exclude='backup/**'
  --exclude='*backup*'
  --exclude='*Backup*'
  --exclude='*BACKUP*'
)

# To include DB/uploads, set env vars: INCLUDE_DB=1 INCLUDE_UPLOADS=1
INCLUDE_DB="${INCLUDE_DB:-0}"
INCLUDE_UPLOADS="${INCLUDE_UPLOADS:-0}"
INCLUDE_CODE="${INCLUDE_CODE:-0}"
if [[ "$INCLUDE_UPLOADS" != "1" ]]; then EXCLUDES+=(--exclude='storage/data/uploads'); fi

# Optionally archive project files (mostly configuration/templates)
if [[ "$INCLUDE_CODE" = "1" ]]; then
  OUT="$OUT_DIR/vpc-app-$TS.tar.gz"
  echo "==> Archiving project files to: $OUT"
  tar "${EXCLUDES[@]}" -czf "$OUT" .
  CODE_ARCHIVE="$OUT"
else
  echo "==> Skipping project code archive (set INCLUDE_CODE=1 to include)"
fi

# Backend detection from env or .env
BACKEND="${DB_BACKEND:-}"
if [[ -z "$BACKEND" && -f .env ]]; then
  BACKEND=$(grep -E '^DB_BACKEND=' .env | head -n1 | cut -d= -f2- | tr -d '\r' | tr '[:upper:]' '[:lower:]')
fi
BACKEND="${BACKEND:-postgres}"
if [[ "$BACKEND" != "postgres" ]]; then
  echo "ERROR: PowderApp now requires Postgres. Set DB_BACKEND=postgres." >&2
  exit 1
fi

# Optionally include database dump
DUMP_PATH=""
if [[ "$INCLUDE_DB" = "1" ]]; then
  # Read PG connection from env or .env
  PGHOST_="${PGHOST:-}"; PGPORT_="${PGPORT:-}"; PGDATABASE_="${PGDATABASE:-}"; PGUSER_="${PGUSER:-}"; PGPASSWORD_="${PGPASSWORD:-}"
  if [[ -z "$PGHOST_" && -f .env ]]; then PGHOST_=$(grep -E '^PGHOST=' .env | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGPORT_" && -f .env ]]; then PGPORT_=$(grep -E '^PGPORT=' .env | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGDATABASE_" && -f .env ]]; then PGDATABASE_=$(grep -E '^PGDATABASE=' .env | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGUSER_" && -f .env ]]; then PGUSER_=$(grep -E '^PGUSER=' .env | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  if [[ -z "$PGPASSWORD_" && -f .env ]]; then PGPASSWORD_=$(grep -E '^PGPASSWORD=' .env | head -n1 | cut -d= -f2- | tr -d '\r'); fi
  : "${PGHOST_:?PGHOST not set and not found in .env}"; : "${PGPORT_:?PGPORT not set and not found in .env}"; : "${PGDATABASE_:?PGDATABASE not set and not found in .env}"; : "${PGUSER_:?PGUSER not set and not found in .env}"; : "${PGPASSWORD_:?PGPASSWORD not set and not found in .env}"
  DUMP_PATH="$OUT_DIR/powderapp_${TS}.dump"
  echo "==> Dumping Postgres to: $DUMP_PATH"
  DOCKER_NETWORK_OPT=()
  if [[ -n "${DOCKER_NETWORK:-}" ]]; then
    DOCKER_NETWORK_OPT=(--network "$DOCKER_NETWORK")
  fi
  docker run --rm "${DOCKER_NETWORK_OPT[@]}" -e PGPASSWORD="$PGPASSWORD_" -v "$(pwd)/$OUT_DIR":/backup postgres:17 \
    pg_dump -h "$PGHOST_" -p "${PGPORT_:-5432}" -U "$PGUSER_" -d "$PGDATABASE_" -Fc -f "/backup/$(basename "$DUMP_PATH")"
fi

# Optionally include uploads archive
UP_OUT=""
if [[ "$INCLUDE_UPLOADS" = "1" && -d storage/data/uploads ]]; then
  UP_OUT="$OUT_DIR/uploads_${TS}.tar.gz"
  echo "==> Archiving uploads to: $UP_OUT"
  tar -czf "$UP_OUT" -C storage/data uploads
fi

echo
echo "✓ Backup artifacts:"
if [[ -n "$CODE_ARCHIVE" ]]; then echo "   $CODE_ARCHIVE"; fi
if [[ -n "$DUMP_PATH" ]]; then echo "   $DUMP_PATH"; fi
if [[ -n "$UP_OUT" ]]; then echo "   $UP_OUT"; fi
if [[ -z "$CODE_ARCHIVE$DUMP_PATH$UP_OUT" ]]; then echo "   (none created)"; fi
echo
echo "Tip: include code, DB, and uploads as needed:"
echo "   INCLUDE_CODE=1 INCLUDE_DB=1 INCLUDE_UPLOADS=1 bash tools/backup.sh"
