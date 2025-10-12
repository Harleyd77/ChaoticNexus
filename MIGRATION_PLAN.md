# Migration Plan

## Features & Blueprints to Preserve
| Blueprint | Legacy Prefix | Notes |
| --- | --- | --- |
| base | `/` (home redirect) & `/uploads` | Keep file delivery + branding helpers; replace `/nav` with new dashboard once React parity confirmed. |
| auth | `/login`, `/logout` | Retain credential flows but expose as JSON first; move HTML fallback out once SPA is primary. |
| react_frontend | `/react` | Continue serving SPA bundle until front-end build moved under new pipeline. |
| customer_portal | `/customer` | Critical for customer self-service; rework forms into services/repos and HTMX-friendly templates. |
| customers | `/customers`, `/api/customers`, `/admin/customer-accounts` | Drives admin customer UI and APIs; migrate to new blueprint naming (`customers`). |
| jobs | `/jobs`, `/api/jobs` | Core job board workflows; keep all operations, convert data access into repositories. |
| powders | `/powders`, `/powders/*.json` | Keep catalogue CRUD + CSV import; align uploads with new storage helpers. |
| inventory | `/inventory`, `/inventory/api/*` | Keep inventory adjustments & history; convert to HTMX-friendly endpoints if desired. |
| sprayer | `/sprayer/*` | Preserve batch tracking; modernise templates and surface metrics via services. |
| admin | `/admin`, `/config/*` | Continue to manage settings, branding, permissions with stronger validation + storage layer. |
| print_templates | `/api/print-templates*` | Keep JSON-driven template manager; ideal candidate for repository/service split. |
| migrate (selected) | none | Convert useful schema upgrade logic to Alembic migrations; drop HTTP exposure. |

## Core Models / Services / Repositories
- **Models** (SQLAlchemy): `User`, `CustomerAccount`, `Customer`, `Contact`, `Job`, `JobPhoto`, `JobEditHistory`, `Powder`, `JobPowder`, `SprayBatch`, `SprayBatchJob`, `PowderUsage`, `InventoryLog`, `ReorderSetting`, `Setting`, `PrintTemplate`.
- **Repositories**: one per aggregate (`customer_repo`, `job_repo`, `powder_repo`, `inventory_repo`, `sprayer_repo`, `settings_repo`, `print_template_repo`). Each returns domain objects / dataclasses, not ORM sessions.
- **Services**: orchestrate workflows: `auth_service`, `customer_service`, `job_service`, `powder_service`, `inventory_service`, `sprayer_service`, `admin_service`, `print_template_service`.
- Shared helpers: storage service for uploads, notification hooks (future), audit logging mixins.

## Items to Drop or Archive
| Path | Reason |
| --- | --- |
| `ChaoticNexus-Orig/blueprints/dev.py` & related templates | Dev-only diagnostics; replace with pytest + health check blueprint if required. |
| `ChaoticNexus-Orig/blueprints/migrate.py` | HTTP-triggered migration is unsafe; port logic into Alembic revision. |
| Backup / experimental templates (`*.bak`, `intake_form.backup.html`, `intake_form.test.html`, `react_demo.html`) | Superseded or redundant once new layout exists. |
| Root binaries & cloudflared artefacts | Environment specific; document infra separately. |
| Legacy SQLite branches in `core/db.py`, `sprayer.py` | Postgres is the official target; remove dual-backend code. |
| Static bundles under `src/powder_app/static/dist` | Rebuild from modern pipeline under `frontend/` and serve via WhiteNoise/Blueprint. |
| CSV tooling superseded by repository/service modules (migrate into CLI commands). |

## Migration Steps
1. **Scaffold** the new backend skeleton (`app/models`, `repositories`, `services`, blueprints) using the provided scaffolding script; move React prototype to `frontend/`.
2. **Model Definitions**: translate legacy schema to SQLAlchemy models; generate initial Alembic migration reflecting current production state.
3. **Repository Layer**: encode existing SQL queries into repository methods; back them with SQLAlchemy sessions.
4. **Service Layer**: port business rules from legacy blueprints/services, calling repositories and emitting events/logs.
5. **Blueprint Reimplementation**: recreate required routes in the new blueprint folders, returning Jinja templates or JSON/HTMX responses. Keep URL signatures stable.
6. **Template Migration**: copy only the templates still in use (customer portal, jobs, admin, etc.), refactor to extend the new base layout and Tailwind partials.
7. **Static Assets**: rebuild Tailwind assets and relocate per-feature CSS/JS into `app/static`; integrate HTMX where appropriate.
8. **Migrations**: convert one-off schema patches (sprayer ensure blocks, migrate endpoint) into Alembic revisions; remove runtime DDL.
9. **Testing & QA**: create pytest suites for services and blueprint smoke tests; include fixture data and golden responses where necessary.
10. **Decommission Legacy**: once feature parity reached, retire `ChaoticNexus-Orig/`, remove unused scripts/assets, and document deployment runbook.
