# Usage: Terminal > Run Task > Deploy to Unraid
# Or: powershell -ExecutionPolicy Bypass -File .\deploy\deploy-unraid.ps1

# --- EDIT THESE VALUES TO MATCH YOUR SETUP ---
$UnraidHost = "192.168.0.207"                 # hostname or IP
$UnraidUser = "root"                          # usually 'root' on Unraid
$RemoteAppDir = "/mnt/user/appdata/PowderApp1.2-experimental"   # where your app lives on Unraid
$RepoUrl     = "https://github.com/Harleyd77/PowderCoatingApp.git"  # your repo
$ContainerName = "PowderApp1.2-Experimental"          # docker container name (target)
$Port        = 5009                            # container mapped port

# --- NO CHANGES NEEDED BELOW ---
$ErrorActionPreference = "Stop"

$DeployDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $DeployDir "..")

Write-Host "[*] Project root: $ProjectRoot"
Write-Host "[*] Unraid: $UnraidUser@${UnraidHost}:${RemoteAppDir}  (port $Port)"
Write-Host "[*] Repo: $RepoUrl"

$rebuildTemplate = @'
#!/bin/bash
set -euo pipefail

REPO_URL="__REPO_URL__"
APP_DIR="__REMOTE_APP_DIR__"
PORT="__PORT__"

APP_NAME="__CONTAINER_NAME__"
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
'@

$rebuild = $rebuildTemplate.Replace("__REPO_URL__", $RepoUrl).Replace("__REMOTE_APP_DIR__", $RemoteAppDir).Replace("__PORT__", $Port.ToString()).Replace("__CONTAINER_NAME__", $ContainerName)
$rebuild = $rebuild.Replace("`r`n", "`n")

$LocalRebuildPath = Join-Path $DeployDir "rebuild.sh"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($LocalRebuildPath, $rebuild, $utf8NoBom)
Write-Host "[*] Created local rebuild.sh: $LocalRebuildPath"

# Ensure remote folder exists
ssh "$UnraidUser@$UnraidHost" "mkdir -p '$RemoteAppDir'"

# Copy rebuild.sh to server
scp "$LocalRebuildPath" "$UnraidUser@${UnraidHost}:${RemoteAppDir}/rebuild.sh"

# Copy .env if present (not tracked in git)
$LocalEnv = Join-Path $ProjectRoot ".env"
if (Test-Path $LocalEnv) {
  Write-Host "[*] Found local .env, copying to server..."
  scp "$LocalEnv" "$UnraidUser@${UnraidHost}:${RemoteAppDir}/.env"
} else {
  Write-Host "[i] No local .env found (skipping). Ensure one exists on the server."
}

# Make executable & run
ssh "$UnraidUser@$UnraidHost" "chmod +x '$RemoteAppDir/rebuild.sh' && bash '$RemoteAppDir/rebuild.sh'"

Write-Host "[OK] Deploy complete."
