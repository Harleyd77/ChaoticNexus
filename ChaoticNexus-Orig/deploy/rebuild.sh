#!/bin/bash
set -euo pipefail

REPO_URL="https://github.com/Harleyd77/PowderCoatingApp.git"
APP_DIR="/mnt/user/appdata/PowderApp1.2-experimental"
PORT="5009"

APP_NAME="PowderApp1.2-Experimental"
IMAGE_NAME="${APP_NAME// /_}"; IMAGE_NAME="${IMAGE_NAME,,}:latest"
ENV_FILE=".env"

echo "[*] Working in: $APP_DIR"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

if [ -d .git ]; then
  echo "[*] Pulling latest..."
  git fetch --all
  git reset --hard origin/main
else
  echo "[*] Cloning fresh repo..."
  git clone "$REPO_URL" .
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "[!] Missing $APP_DIR/$ENV_FILE. Deployment requires an env file." >&2
  exit 1
fi

if ! grep -q '^DB_BACKEND=postgres' "$ENV_FILE"; then
  echo "[!] Expected DB_BACKEND=postgres in $ENV_FILE." >&2
  exit 1
fi

if [ -f docker-compose.yml ] || [ -f docker-compose.yaml ]; then
  echo "[*] docker compose up -d --build"
  if command -v docker compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
  elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
  else
    echo "[!] docker compose file present but no docker compose binary found." >&2
    exit 1
  fi
  "${COMPOSE_CMD[@]}" pull
  "${COMPOSE_CMD[@]}" up -d --build
  echo "[OK] Compose redeploy complete."
  exit 0
fi

echo "[*] Building image..."
docker build -t "$IMAGE_NAME" .

echo "[*] Restarting container..."
docker stop "$APP_NAME" >/dev/null 2>&1 || true
docker rm "$APP_NAME" >/dev/null 2>&1 || true

DATA_DIR="${DATA_DIR:-$APP_DIR/storage/data}"
UPLOADS_DIR="${UPLOADS_DIR:-}"
echo "[*] Using data dir: $DATA_DIR"
mkdir -p "$DATA_DIR"

MOUNTS=(-v "$DATA_DIR:/app/storage/data")

if [ -n "$UPLOADS_DIR" ]; then
  echo "[*] Using uploads dir override: $UPLOADS_DIR"
  mkdir -p "$UPLOADS_DIR"
  MOUNTS+=(-v "$UPLOADS_DIR:/app/storage/data/uploads")
fi

docker run -d --name "$APP_NAME" --restart unless-stopped -p "$PORT":5000 --env-file "$ENV_FILE" "${MOUNTS[@]}" "$IMAGE_NAME"

echo "[OK] Done. App should be on http://$(hostname -f 2>/dev/null || hostname):$PORT/"