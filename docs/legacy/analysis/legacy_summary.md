# analysis/legacy_summary.md
# Legacy PowderApp Summary

## Entry Points & Stack
- Runtime entry is `src/powder_app/main.py`; it imports the `create_app()` factory from `src/powder_app/__init__.py`.
- `create_app()` wires core services (`core.config`, `core.db`, `core.security`, template helpers) and registers every blueprint before attaching a global `before_request` auth guard.
- The app targets Postgres 16 and Python 3.11. SQLite compatibility helpers still exist but `core.db.init_db()` now raises if Postgres is not configured.
- Static assets are served from `src/powder_app/static` (classic CSS/JS plus a built React bundle under `static/dist`). React source lives in `frontend/` (Vite + Tailwind), but build artifacts are copied into `static/dist`.

## Blueprint Map & Recommendations
| Blueprint | Purpose | Notable Routes | Recommendation |
| --- | --- | --- | --- |
| `base` | Legacy navigation page, favicon override, uploads serving | `/nav`, `/uploads/<path>` | Keep upload + branding helpers; retire `/nav` once new UI replaces it. |
| `auth` | Admin & customer login/logout (HTML form fallbacks) | `/login`, `/logout`, `/login/customer` | Retain API-compatible POST handling; phase out template rendering in favor of React login. |
| `react_frontend` | Serves React SPA bundle and login API | `/react/*`, `/react/api/login` | Keep as bridge while React UI is primary surface; ensure build pipeline continues to publish to `static/dist`. |
| `customer_portal` | Customer self-service (register, dashboard, edit jobs, submit jobs) | `/customer/register`, `/customer/jobs/*`, `/customer/profile` | Keep and modernize: logic is business-critical but should migrate to service layer / API + SPA views. |
| `intake` | Public powder/railing intake forms + file uploads | `/intake_form`, `/railing_intake`, `/submit` | Legacy flow duplicated by portal; plan to deprecate once portal submission is proven. |
| `customers` | Admin customer management + contacts API | `/customers`, `/api/customers`, `/admin/customer-accounts/*` | Keep functionality; refactor into API layer. Currently powers new React customers UI. |
| `jobs` | Jobs board, Kanban, work orders, CSV export, photo uploads | `/jobs*`, `/api/jobs/kanban/move` | Core operations; keep but break into services and REST endpoints before porting UI. |
| `powders` | Powder catalog CRUD + CSV import/export | `/powders*` | Keep, but consolidate upload/import logic and share with inventory module. |
| `inventory` | Stock adjustments, history, reorder summary | `/inventory*`, `/inventory/api/*` | Keep; already structured like an API—good candidate to reuse in new stack. |
| `sprayer` | Batch tracking for spray booth + powder usage | `/sprayer/*` | Keep domain logic but extract to dedicated module; routes rely on legacy templates. |
| `admin` | UI settings, branding uploads, user management | `/admin*`, `/config/*` | Keep features but harden file handling & permissions; UI should move to new front end. |
| `print_templates` | CRUD for JSON print template definitions | `/api/print-templates*` | Keep; pure API, easy to migrate. |
| `migrate` | One-off endpoint adding columns for pricing charges | `/admin/migrate/add-charge-columns` | Drop; replace with proper migration script (already partially handled under `tools/migrations`). |
| `dev` | Dev-only health/checklist endpoints for Chrome MCP extension | `/dev/health`, `/dev/mcp-checklist.json` | Drop from production; keep as local dev tool or port to FastAPI diagnostics if needed. |

## Templates & Static Assets
- Server-rendered templates live under `src/powder_app/templates`; many duplicate or prototype pages (`intake_form.backup.html`, `.test.html`, `react_demo.html`). These can be archived once React pages fully replace them.
- `_components/macros.html` defines reusable form/display components; useful reference if we keep any Jinja surfaces.
- Customer portal and admin templates are the most structured; intake templates are ad hoc and should be retired post-migration.
- Static CSS/JS under `static/` powers theme switching, customer cards, and legacy motion scripts. `static/dist/` contains the built React bundle (`index-*.css`, `main-*.js`) served by the SPA blueprint.

## Data Layer Notes
- No SQLAlchemy models exist; persistence relies on raw SQL helpers in `core/db.py` that build schema at runtime. Additional ensure/alter logic appears in `sprayer.py`.
- Tables cover jobs, powders, customers/contacts, users, customer portal accounts/sessions, inventory logs, print templates, and spray batches. Relationships are enforced via foreign keys in Postgres only.
- Legacy SQLite migration helpers remain but should be deleted once confirmed unused.
- Manual migration scripts reside in `tools/migrations/`; convert these into real Alembic/SQL migrations before future changes.

## Other Artifacts
- `frontend/` (React/Vite project) is the new UI source. Its build output must continue to land in `static/dist` until the Flask app stops serving assets directly.
- `storage/data/` contains uploaded files and CSV exports; treat as persistent volume in Docker.
- Numerous Markdown guides (`IMPLEMENTATION_SUMMARY.md`, `THEME_SYSTEM_SETUP.md`, etc.) describe historical work. Keep for knowledge transfer unless superseded.
- `cloudflared*` binaries/configs in root look environment-specific; safe to drop from the repository.

## Keep / Modernize / Drop Snapshot
- **Keep & Modernize**: `core` helpers (config, db, security, uploads, template utils), blueprints `customers`, `jobs`, `powders`, `inventory`, `sprayer`, `admin`, `customer_portal`, `react_frontend`, `print_templates`.
- **Monitor / Replace**: `intake` forms (replace with portal + API), legacy Jinja templates for nav/jobs/customers once React equivalents ship.
- **Drop Soon**: Blueprints `migrate` and `dev`; stray backup templates (`*.backup.html`, `.test.html`), root binaries (`cloudflared*`), SQLite fallbacks, and obsolete docs once merged into new handbook.

## Immediate Migration Ideas
1. Extract data access into dedicated service modules (start with jobs/customers) to prepare for an API-first rewrite.
2. Introduce a real migration tool and port the `tools/migrations` scripts + ad-hoc schema patches into versioned migrations.
3. Harden file handling (uploads, branding assets) and move them behind authenticated APIs before replacing the Jinja-based admin UI.
4. Decide on the future of intake: either wrap `/submit` behind the customer portal or remove the public form entirely.
