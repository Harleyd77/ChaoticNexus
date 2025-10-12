#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"
OUT="${2:-status_report.txt}"
{
  echo "== Chaotic Nexus Status Report =="
  echo "Generated: $(date -Iseconds)"
  echo "Root: $ROOT"
  echo
  echo "## Tree (top 2 levels)"
  find "$ROOT" -maxdepth 2 -mindepth 1 -type d -printf '%p/\n' | sort
  echo
  echo "## Key files"
  for f in compose.yaml docker-compose.yml .env app/wsgi.py app/__init__.py app/Dockerfile; do
    [ -f "$ROOT/$f" ] && echo "OK  - $f" || echo "MISS- $f"
  done
  echo
  echo "## Docker compose ps"
  (cd "$ROOT" && docker compose ps) || echo "compose ps failed"
  echo
  echo "## Web log tail (last 60)"
  (cd "$ROOT" && docker compose logs --no-color --tail=60 web) || echo "no web logs"
  echo
  echo "## Postgres log tail (last 40)"
  (cd "$ROOT" && docker compose logs --no-color --tail=40 postgres) || echo "no postgres logs"
  echo
  echo "## Expected URLs"
  IP=$(hostname -I | awk '{print $1}')
  echo "Health:   http://$IP:8080/healthz"
  echo "Dashboard http://$IP:8080/dashboard/"
} > "$OUT"
echo "Wrote $OUT"
