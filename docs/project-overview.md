# Chaotic Nexus Project Overview

## Product Mission

Chaotic Nexus is an operations hub for a powder-coating shop. The goal is to keep job intake, production coordination, inventory tracking, and customer self-service in a single system with consistent UI patterns.

## Primary User Groups

- **Production staff (internal):** Work from the Flask “Operations Hub” dashboard at `/dashboard/` to launch intake flows, manage batches, and review jobs.
- **Administrators:** Configure settings, review metrics, and oversee records via the same admin-facing Flask blueprints (jobs, customers, powders, sprayer, etc.).
- **Customers:** Access the customer portal at `/customer/` to view job status, submit requests, and manage their own data.
- **Future SPA users:** The React/Vite frontend in `app/src/` is currently a prototype dashboard; keep it only if we expand to a richer SPA experience.

## High-Level Architecture

- **Flask application (`app/`):**
  - `app/__init__.py` bootstraps the app factory and registers blueprints.
  - `app/blueprints/` holds feature blueprints (`dashboard`, `jobs`, `customer_portal`, `intake`, etc.) each with `views.py`, optional `service.py`, and Jinja templates.
  - `app/templates/` contains shared layouts (`_layouts/base.html`) and partials (`_partials/header.html`, `_macros/ui.html`).
  - `app/static/` serves compiled Tailwind CSS, Alpine/HTMX helpers, and shared JS modules.
- **Service & data layers:**
  - `app/models/`, `app/repositories/`, and `app/services/` establish the layered architecture even when portions are still stubs.
- **React prototype (`app/src/`):** A Vite-powered SPA with a demo dashboard (`pages/Dashboard.jsx`). It uses shared components under `app/src/components/`.
- **Infrastructure & config:** Docker compose, Gunicorn config, Tailwind/PostCSS settings, and migrations live at the repository root.

## Core Dashboards & Entry Points

| Audience | Entry URL | Notes |
| --- | --- | --- |
| Staff/admin | `/dashboard/` | Flask Operations Hub, permission-gated sections powered by `app/blueprints/dashboard/views.py` and `templates/dashboard/index.html`. |
| Customers | `/customer/` | Customer portal blueprint with its own layout and dashboards under `app/blueprints/customer_portal/`. |
| React prototype | `/` (SPA) | Vite-served dashboard placeholder. Registered in `app/src/App.tsx`. |

## Reference Documents

- `PROJECT_STANDARDS.md` – stack, directory conventions, and layering rules.
- `MIGRATION_PLAN.md` – blueprint migration checklist and service/repository goals.
- `DEVTOOLS_FINDINGS.md` – ongoing QA findings from Playwright/DevTools sessions.
- `docs/current-focus.md` – living document of active goals (created alongside this overview).
- Archived legacy guidance is kept under `docs/archive/` once superseded.

## Guiding Principles

1. Keep Flask blueprints as the authoritative experience unless there’s a clear need for the SPA.
2. Use shared UI primitives (macros and upcoming `btn-*` utilities) to ensure consistent styling.
3. Document decisions and active work in `docs/current-focus.md` to avoid repeating context every session.

