# Database Gaps & Safety Rails

Track DB-related issues encountered during tests/devtools, and propose minimal, forward-only fixes.

| Table/Column | Error | One-line Fix | Status |
| --- | --- | --- | --- |
| jobs.current_stage | missing enum value 'QA' | Alembic migration: add enum value 'QA' | ❌ |
| inventory_log | table missing | Alembic migration: create table if not exists | ❌ |
| reorder_settings | table missing | Alembic migration: create table if not exists | ❌ |
| job_photos | table missing | Alembic migration: create table if not exists | ❌ |
| job_edit_history | table missing | Alembic migration: create table if not exists | ❌ |
| print_templates | table missing | Alembic migration: create table if not exists | ❌ |
| view_jobs_compat | view missing | Create read-only view mapping legacy columns | ❌ |

Safety rails:
- Idempotent migrations: treat existing objects as success.
- Seed admin user and minimal lookups to avoid NOT NULL/FK errors.
- No runtime DDL in app code.

