#!/usr/bin/env bash
set -euo pipefail

# Project root = parent of this script's folder
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="powderapp:1.3"       # local image tag
CONTAINER="PowderApp1.3"    # container name can stay mixed case
PORT="${PORT:-5001}"        # host port -> container 5000
ENV_FILE=".env"
# Use a host bind mount for persistent data (no named volume)
# Set DATA_DIR explicitly or it defaults to the repo's storage/data
DATA_DIR="${DATA_DIR:-$APP_DIR/storage/data}"

NETWORK_NAME="${NETWORK_NAME:-powderapp13_default}"
PGHOST_CONTAINER="${PGHOST_CONTAINER:-powderapp13-postgres-1}"
declare -a EXTRA_RUN_ARGS=()

if docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  echo "==> Attaching to Docker network: $NETWORK_NAME"
  EXTRA_RUN_ARGS+=(--network "$NETWORK_NAME")
else
  echo "==> Docker network '$NETWORK_NAME' not found; using default bridge network"
fi

if [[ -n "$PGHOST_CONTAINER" ]]; then
  echo "==> Overriding PGHOST inside container -> $PGHOST_CONTAINER"
  EXTRA_RUN_ARGS+=(-e "PGHOST=$PGHOST_CONTAINER")
fi

cd "$APP_DIR"

echo "==> Building image: $IMAGE"
docker build -t "$IMAGE" .

echo "==> Stopping old container (if any)"
docker stop "$CONTAINER" >/dev/null 2>&1 || true
docker rm "$CONTAINER"  >/dev/null 2>&1 || true

echo "==> Using host bind mount for data: $DATA_DIR -> /app/storage/data"
mkdir -p "$DATA_DIR"
MOUNT_DATA="-v ${DATA_DIR}:/app/storage/data"

# Optional: separate uploads directory (centralized photos)
UPLOADS_DIR="${UPLOADS_DIR:-}"
MOUNT_UPLOADS=""
if [[ -n "$UPLOADS_DIR" ]]; then
  echo "==> Using separate uploads dir: $UPLOADS_DIR -> /app/storage/data/uploads"
  mkdir -p "$UPLOADS_DIR"
  MOUNT_UPLOADS="-v ${UPLOADS_DIR}:/app/storage/data/uploads"
fi

echo "==> Starting container: $CONTAINER (host port ${PORT})"
# Mount full app source read-only for live template/static edits,
# and mount a separate writable volume for persistent data.
docker run -d --name "$CONTAINER" \
  --restart unless-stopped \
  -p ${PORT}:5000 \
  --env-file "$ENV_FILE" \
  -e GUNICORN_RELOAD=1 \
  ${EXTRA_RUN_ARGS[@]+"${EXTRA_RUN_ARGS[@]}"} \
  -v "$APP_DIR":/app:ro \
  ${MOUNT_DATA} \
  ${MOUNT_UPLOADS} \
  "$IMAGE"

echo "==> Container status:"
docker ps --filter "name=$CONTAINER" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# Quick sanity check: verify data mount and DB path inside the container
echo "==> Verifying data mount and DB path in container"
docker exec "$CONTAINER" sh -lc "ls -lah /app/storage/data /app/storage/data/uploads 2>/dev/null || true"
docker exec "$CONTAINER" python -c "import os, sys; sys.path.insert(0,'/app/src'); import powder_app.main as m; print('DB_PATH:', m.DB_PATH); print('DB exists:', os.path.exists(m.DB_PATH))" 2>/dev/null || true

IP=$(hostname -I 2>/dev/null | awk '{print $1}')
[ -z "$IP" ] && IP="<UNRAID-IP>"
echo "==> Done. Open: http://$IP:${PORT}/nav"
