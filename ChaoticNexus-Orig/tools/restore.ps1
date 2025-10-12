param(
  [Parameter(Mandatory=$true)][string]$Source,
  [switch]$IncludeUploads
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Container = $env:CONTAINER; if (-not $Container) { $Container = "PowderApp1.2" }
$DataDir = $env:DATA_DIR; if (-not $DataDir) { $DataDir = Join-Path $Root 'storage/data' }
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

# Detect backend from env/.env
$backend = $env:DB_BACKEND
if (-not $backend -and (Test-Path ".env")) {
  $line = (Select-String -Path .env -Pattern '^DB_BACKEND=' | Select-Object -First 1).Line
  if ($line) { $backend = $line.Split('=')[1].Trim().ToLower() }
}
if (-not $backend) { $backend = 'postgres' }

if ($backend -ne 'postgres') { throw 'PowderApp now requires Postgres. Set DB_BACKEND=postgres.' }

# Stop app container if running
try { docker stop $Container | Out-Null } catch { }

function Restore-PostgresDump($dumpFile) {
  $pgHost = $env:PGHOST; if (-not $pgHost) { $l = (Select-String -Path .env -Pattern '^PGHOST=' | Select-Object -First 1).Line; if ($l) { $pgHost = $l.Split('=')[1].Trim() } }
  $pgPort = $env:PGPORT; if (-not $pgPort) { $l = (Select-String -Path .env -Pattern '^PGPORT=' | Select-Object -First 1).Line; if ($l) { $pgPort = $l.Split('=')[1].Trim() } }
  $pgDb   = $env:PGDATABASE; if (-not $pgDb) { $l = (Select-String -Path .env -Pattern '^PGDATABASE=' | Select-String -First 1).Line; if ($l) { $pgDb = $l.Split('=')[1].Trim() } }
  $pgUser = $env:PGUSER; if (-not $pgUser) { $l = (Select-String -Path .env -Pattern '^PGUSER=' | Select-Object -First 1).Line; if ($l) { $pgUser = $l.Split('=')[1].Trim() } }
  $pgPass = $env:PGPASSWORD; if (-not $pgPass) { $l = (Select-String -Path .env -Pattern '^PGPASSWORD=' | Select-Object -First 1).Line; if ($l) { $pgPass = $l.Split('=')[1].Trim() } }
  if (-not $pgHost -or -not $pgDb -or -not $pgUser -or -not $pgPass) { throw "Missing PG env; set in .env or environment" }
  $dir = Split-Path -Parent $dumpFile
  $name = Split-Path -Leaf $dumpFile
  docker run --rm -e "PGPASSWORD=$pgPass" -v "$dir:/backup" postgres:17 pg_restore -h $pgHost -p $pgPort -U $pgUser -d $pgDb --clean --if-exists --no-owner "/backup/$name"
}

function Restore-PostgresSql($sqlFile) {
  $pgHost = $env:PGHOST; if (-not $pgHost) { $l = (Select-String -Path .env -Pattern '^PGHOST=' | Select-Object -First 1).Line; if ($l) { $pgHost = $l.Split('=')[1].Trim() } }
  $pgPort = $env:PGPORT; if (-not $pgPort) { $l = (Select-String -Path .env -Pattern '^PGPORT=' | Select-Object -First 1).Line; if ($l) { $pgPort = $l.Split('=')[1].Trim() } }
  $pgDb   = $env:PGDATABASE; if (-not $pgDb) { $l = (Select-String -Path .env -Pattern '^PGDATABASE=' | Select-Object -First 1).Line; if ($l) { $pgDb = $l.Split('=')[1].Trim() } }
  $pgUser = $env:PGUSER; if (-not $pgUser) { $l = (Select-String -Path .env -Pattern '^PGUSER=' | Select-Object -First 1).Line; if ($l) { $pgUser = $l.Split('=')[1].Trim() } }
  $pgPass = $env:PGPASSWORD; if (-not $pgPass) { $l = (Select-String -Path .env -Pattern '^PGPASSWORD=' | Select-Object -First 1).Line; if ($l) { $pgPass = $l.Split('=')[1].Trim() } }
  if (-not $pgHost -or -not $pgDb -or -not $pgUser -or -not $pgPass) { throw "Missing PG env; set in .env or environment" }
  $dir = Split-Path -Parent $sqlFile
  $name = Split-Path -Leaf $sqlFile
  docker run --rm -e "PGPASSWORD=$pgPass" -v "$dir:/backup" postgres:17 psql -h $pgHost -p $pgPort -U $pgUser -d $pgDb -f "/backup/$name"
}

# If zip, extract to temp folder
$Tmp = $null
$SrcPath = $null
if (Test-Path $Source -PathType Leaf -and $Source.ToLower().EndsWith('.zip')) {
  $Tmp = New-Item -ItemType Directory -Path ([System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), [System.IO.Path]::GetRandomFileName()))
  Expand-Archive -Path $Source -DestinationPath $Tmp.FullName -Force
  $SrcPath = $Tmp.FullName
}
elseif (Test-Path $Source -PathType Container) {
  $SrcPath = $Source
}
else {
  $SrcPath = Split-Path -Parent $Source
}

switch ($backend) {
  'postgres' {
    if ($Source.ToLower().EndsWith('.dump')) { Restore-PostgresDump $Source }
    elseif ($Source.ToLower().EndsWith('.sql')) { Restore-PostgresSql $Source }
    else {
      $dump = Get-ChildItem -Path $SrcPath -Recurse -Filter *.dump | Select-Object -First 1
      if ($dump) { Restore-PostgresDump $dump.FullName }
      elseif (Test-Path (Join-Path $SrcPath 'app.db')) {
        # Run migration script inside python container
        $pgHost = $env:PGHOST; if (-not $pgHost) { $l = (Select-String -Path .env -Pattern '^PGHOST=' | Select-Object -First 1).Line; if ($l) { $pgHost = $l.Split('=')[1].Trim() } }
        $pgPort = $env:PGPORT; if (-not $pgPort) { $l = (Select-String -Path .env -Pattern '^PGPORT=' | Select-Object -First 1).Line; if ($l) { $pgPort = $l.Split('=')[1].Trim() } }
        $pgDb   = $env:PGDATABASE; if (-not $pgDb) { $l = (Select-String -Path .env -Pattern '^PGDATABASE=' | Select-Object -First 1).Line; if ($l) { $pgDb = $l.Split('=')[1].Trim() } }
        $pgUser = $env:PGUSER; if (-not $pgUser) { $l = (Select-String -Path .env -Pattern '^PGUSER=' | Select-Object -First 1).Line; if ($l) { $pgUser = $l.Split('=')[1].Trim() } }
        $pgPass = $env:PGPASSWORD; if (-not $pgPass) { $l = (Select-String -Path .env -Pattern '^PGPASSWORD=' | Select-Object -First 1).Line; if ($l) { $pgPass = $l.Split('=')[1].Trim() } }
        docker run --rm -it -e "PGPASSWORD=$pgPass" -v "$Root:/app" -w /app python:3.11-slim bash -lc "pip install --no-cache-dir psycopg[binary]==3.2.1 > /dev/null && python tools/migrate_sqlite_to_postgres.py --host '$pgHost' --port '$pgPort' --db '$pgDb' --user '$pgUser' --sqlite '$($SrcPath)/app.db'"
      }
      else { throw "Could not find .dump or app.db in $Source" }
    }
  }
  default { throw 'PowderApp now requires Postgres. Set DB_BACKEND=postgres.' }
}

# Restart container
try { docker start $Container | Out-Null } catch { }

Write-Host "Restore complete. Check /admin/dbinfo in the app."

