# Project Standards

## Stack
- Python 3.11
- Flask (app factory pattern only)
- SQLAlchemy with Alembic for database migrations
- Postgres 16 as the single database target
- Gunicorn for production WSGI
- Docker + Docker Compose v2 for orchestration
- Tailwind CSS for styling; generated assets live under `app/static/css`
- HTMX (and Alpine.js only when necessary) for incremental interactivity
- Optional Flask-WTF for server-side forms
- pytest for testing, with coverage targets agreed per feature
- Tooling: ruff, black, isort for lint/format, pre-commit hooks encouraged

## Authoritative Layout
```
app/
  __init__.py
  config.py
  extensions.py
  models/
  repositories/
  services/
  blueprints/
    <feature>/
      __init__.py
      views.py
      service.py
      forms.py (optional)
      templates/<feature>/
      static/<feature>/
  templates/
    _layouts/
      base.html
    _partials/
  static/
    css/
    js/
    img/
  cli.py
migrations/
PROJECT_STANDARDS.md
MIGRATION_PLAN.md
app/gunicorn.conf.py
compose.yaml
.env (non-committed example values in `.env.example`)
```
- The React prototype currently under `app/` will be relocated to `frontend/` during the migration; new backend files follow the structure above.

## Application Factory & Extensions
- `app/__init__.py` exports `create_app(config_name: str | None = None)`.
- App factory responsibilities:
  - Load configuration via `app/config.py`.
  - Initialise extensions from `app/extensions.py` (db, migrate, login, csrf, etc.).
  - Register blueprints from `app/blueprints/*/__init__.py`.
  - Register CLI commands from `app/cli.py`.
  - Attach error handlers and request hooks (if any) via dedicated modules.
- Extensions are initialised once in `extensions.py` and imported everywhere else through that module.

## Blueprint & Layering Rules
- Each blueprint folder holds HTTP concerns only:
  - `views.py`: request handlers returning responses; no business logic or DB calls.
  - `service.py`: orchestrates calls into repositories and other services.
  - `forms.py`: optional Flask-WTF forms for that feature.
  - `templates/<feature>` and `static/<feature>` contain feature-specific UI assets.
- Cross-feature services live in `app/services/` and must remain framework agnostic.
- Repositories encapsulate SQLAlchemy queries and sit behind service interfaces.
- No raw SQL in views or services. All database changes are expressed via SQLAlchemy models.
- Blueprints are registered only inside the app factory.

## Data & Migrations
- Define every table as a SQLAlchemy model under `app/models/`.
- All schema changes require Alembic migrations (`migrations/`); never use ad-hoc DDL in code.
- Seed or maintenance scripts belong in `app/cli.py` or `tools/` modules.

## UI Standards
- Shared layout at `app/templates/_layouts/base.html` with Tailwind utilities.
- Reusable partials go under `app/templates/_partials/`.
- Feature templates extend the base layout.
- HTMX used sparingly for progressive enhancement; reach for Alpine.js only when state is local and simple.
- No new heavyweight JavaScript frameworks without architectural approval.

## Configuration & Environment
- Environment variables read in `config.py`; default config classes: `BaseConfig`, `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`.
- `.env` (not committed) stores local defaults; reference template `.env.example` documents required settings.
- Logging configured via `logging.dictConfig` inside `create_app` and respects `LOG_LEVEL` env variable.
- Secrets never stored in source control.

## Testing & Quality
- pytest as the testing framework; tests live under `tests/` mirroring the app package structure.
- Each service/repository requires unit coverage; blueprints need integration tests (via Flask test client).
- Use `pytest --cov` for coverage; minimum thresholds agreed per milestone.
- Ruff handles linting (configured in `pyproject.toml`), black for formatting, isort for import order.
- Pre-commit configuration ensures consistent tooling.

## Deployment & Compose Policy
- Official Compose file: `compose.yaml` (version 2).
- Services: `web` (Flask/Gunicorn), `db` (Postgres 16), optional `worker`.
- Volumes: map `./pgdata` → Postgres data, `./_logs` → app logs, `./_data` → shared uploads.
- Port mapping: host `8080` → container `8000` for the Flask web service.
- Gunicorn configuration at `app/gunicorn.conf.py` uses environment variable `PORT` for bind address.

## Dependency Management
- Use `pyproject.toml` + `poetry` or `requirements/*.txt` with pins; document chosen approach.
- Reuse existing dependencies where possible; new dependencies require a short justification in PR description and follow semantic version pinning.
- Remove unused packages during migration to keep the footprint lean.

## Workflow & Collaboration
- Conventional Commits (`feat:`, `fix:`, `chore:` etc.) for commit messages.
- Pull Requests must outline:
  1. Why (context / problem)
  2. What changed (summary)
  3. Tests (list commands or explain gaps)
  4. Screenshots / API samples / migration outputs when applicable
  5. Migration considerations (schema, data backfills)
- CI validates linting, formatting, tests, and migration consistency before merge.
- Code reviews focus on adherence to these standards and maintainable design.
