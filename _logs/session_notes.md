
# Session Notes - Chrome MCP Setup & Migration State

## Infrastructure
- Docker stack: `docker compose up -d web postgres` (web serves `/healthz`).
- Compose points at repo root with Dockerfile `app/Dockerfile`; `.env` uses `postgresql+psycopg://`.

## Tooling
- Node managed via nvm (default `v20.19.5`). MCP binary: `~/.nvm/versions/node/v20.19.5/bin/chrome-devtools-mcp`.
- MCP config: `~/.mcp/servers/usrlocal.chromedevtools/chrome-devtools-mcp` pointing at `http://localhost:8080`.

## Next Steps
1. Port legacy `dev` blueprint (e.g., `/dev/mcp-checklist.json`) into the new Flask app.
2. Start migrating models/repositories/services from `ChaoticNexus-Orig`.
3. Add Alembic migrations as schemas solidify.
