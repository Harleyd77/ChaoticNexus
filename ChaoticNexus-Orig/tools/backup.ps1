param(
  [switch]$IncludeDb,
  [switch]$IncludeUploads
)

$ErrorActionPreference = "Stop"

# Project root = parent of this script's folder
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

# Ensure backups directory
$DestDir = Join-Path $Root "storage/backups/app"
New-Item -ItemType Directory -Force -Path $DestDir | Out-Null

# Timestamp and main zip path
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$ZipPath = Join-Path $DestDir ("vpc-app-" + $Timestamp + ".zip")

# Build exclusion rules
$ex = @(
  "\\.venv(\|$)",
  "\\.git(\|$)",
  "node_modules(\|$)",
  "__pycache__(\|$)",
  "storage[\\/]+backups(\|$)"
)

# Exclude secrets/local data unless explicitly requested
if (-not $IncludeDb) { $ex += "storage[\\/]+data[\\/]+app\.db$" }
if (-not $IncludeUploads) { $ex += "storage[\\/]+data[\\/]+uploads(\|$)" }
$ex += "^\.env$"

# Gather files to include
$files = Get-ChildItem -Recurse -File | Where-Object {
  $path = $_.FullName
  -not ( $ex | ForEach-Object { $path -match $_ } | Where-Object { $_ } )
}

if (-not $files) {
  Write-Host "No files found to back up. Are you in the project folder?"
  exit 1
}

if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
Compress-Archive -Path $files.FullName -DestinationPath $ZipPath

# Optionally include database
$DbArtifact = $null
if ($IncludeDb) {
  # Detect backend
  $backend = $env:DB_BACKEND
  if (-not $backend -and (Test-Path ".env")) {
    $line = (Select-String -Path .env -Pattern '^DB_BACKEND=' | Select-Object -First 1).Line
    if ($line) { $backend = $line.Split('=')[1].Trim() }
  }
  if (-not $backend) { $backend = 'postgres' }
  if ($backend.ToLower() -ne 'postgres') { throw 'PowderApp now requires Postgres. Set DB_BACKEND=postgres.' }
  if ($backend -and $backend.ToLower() -eq 'postgres') {
    $pgHost = $env:PGHOST;      if (-not $pgHost) { $l = (Select-String -Path .env -Pattern '^PGHOST=' | Select-Object -First 1).Line;      if ($l) { $pgHost = $l.Split('=')[1].Trim() } }
    $pgPort = $env:PGPORT;      if (-not $pgPort) { $l = (Select-String -Path .env -Pattern '^PGPORT=' | Select-Object -First 1).Line;      if ($l) { $pgPort = $l.Split('=')[1].Trim() } }
    $pgDb   = $env:PGDATABASE;  if (-not $pgDb)   { $l = (Select-String -Path .env -Pattern '^PGDATABASE=' | Select-Object -First 1).Line;  if ($l) { $pgDb   = $l.Split('=')[1].Trim() } }
    $pgUser = $env:PGUSER;      if (-not $pgUser) { $l = (Select-String -Path .env -Pattern '^PGUSER=' | Select-Object -First 1).Line;      if ($l) { $pgUser = $l.Split('=')[1].Trim() } }
    $pgPass = $env:PGPASSWORD;  if (-not $pgPass) { $l = (Select-String -Path .env -Pattern '^PGPASSWORD=' | Select-Object -First 1).Line;  if ($l) { $pgPass = $l.Split('=')[1].Trim() } }
    if (-not $pgHost -or -not $pgDb -or -not $pgUser -or -not $pgPass) { throw "Missing PG env; set in .env or environment" }
    $dumpName = "powderapp_${Timestamp}.dump"
    $DbArtifact = Join-Path $DestDir $dumpName
    Write-Host "==> Dumping Postgres to: $DbArtifact"
    $didDump = $false
    if (Get-Command docker -ErrorAction SilentlyContinue) {
      docker run --rm -e "PGPASSWORD=$pgPass" -v "${DestDir}:/backup" postgres:17 `
        pg_dump -h $pgHost -p $pgPort -U $pgUser -d $pgDb -Fc -f "/backup/$dumpName"
      $didDump = $true
    }
    elseif (Get-Command pg_dump -ErrorAction SilentlyContinue) {
      $env:PGPASSWORD = $pgPass
      pg_dump -h $pgHost -p $pgPort -U $pgUser -d $pgDb -Fc -f $DbArtifact
      Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
      $didDump = $true
    }
    if (-not $didDump) {
      throw "Neither Docker nor pg_dump found. Install Docker Desktop or PostgreSQL client tools to enable DB backups."
    }
  }
}

# Optionally include uploads
$UploadsZip = $null
if ($IncludeUploads) {
  $upSrc = Join-Path $Root 'storage/data/uploads'
  if (Test-Path $upSrc) {
    $UploadsZip = Join-Path $DestDir ("uploads_" + $Timestamp + ".zip")
    Write-Host "==> Archiving uploads to: $UploadsZip"
    if (Test-Path $UploadsZip) { Remove-Item $UploadsZip -Force }
    Compress-Archive -Path (Join-Path $upSrc '*') -DestinationPath $UploadsZip
  }
}

Write-Host ""
Write-Host "Backup created:" -ForegroundColor Green
Write-Host "   $ZipPath"
if ($DbArtifact) { Write-Host "   $DbArtifact" }
if ($UploadsZip) { Write-Host "   $UploadsZip" }
Write-Host ""
Write-Host "Tip: include DB and uploads:"
Write-Host "   powershell -ExecutionPolicy Bypass -File tools\backup.ps1 -IncludeDb -IncludeUploads"
