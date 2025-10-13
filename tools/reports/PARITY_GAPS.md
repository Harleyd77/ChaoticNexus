# Parity Gaps

List ⚠️/❌ from the Parity Matrix with precise gaps and minimal fixes (no schema changes).

## Base
- Gap: `/nav` redirect not explicit 308.
  - Files: app/__init__.py (root redirect), app/blueprints/dashboard
  - Minimal fix: add `/nav` route returning 308 to `/dashboard/`.
  - Risk: Low; Effort: XS

## Auth
- Gap: Customer logout POST path behavior parity not validated.
  - Files: app/blueprints/auth/views.py, customer_portal/views.py
  - Minimal fix: align methods and redirects; add tests.
  - Risk: Low; Effort: S

## Customer Portal
- Gap: Forgot-password flow stubs only.
  - Files: customer_portal/views.py, services/auth_service.py
  - Minimal fix: no-op stub that mirrors legacy response shape; log TODO.
  - Risk: Low; Effort: S

## Customers
- Gap: Contacts JSON endpoints not present.
  - Files: customers/views.py, services/customer_service.py
  - Minimal fix: add JSON routes backed by service with adapters.
  - Risk: Medium; Effort: M

## Jobs
- Gap: Photos upload/delete, CSV export, screen routes missing.
  - Files: jobs/views.py, services/job_service.py, repositories/job_repo.py
  - Minimal fix: wire endpoints; re-use uploads helper; stream CSV.
  - Risk: Medium; Effort: M

## Powders
- Gap: families/colors/by_color JSON missing; CSV import/export incomplete.
  - Files: powders/views.py, services/powder_service.py
  - Minimal fix: lightweight JSON endpoints; CSV writer/reader parity.
  - Risk: Low; Effort: M

## Inventory
- Gap: reorder/history APIs not wired; adjust/update stubs only.
  - Files: inventory/views.py, inventory_service.py, repositories
  - Minimal fix: implement repo/service; return legacy shapes.
  - Risk: Medium; Effort: M

## Intake
- Gap: production/railing forms and submit persistence missing.
  - Files: intake/views.py, intake_service.py
  - Minimal fix: implement forms/validation and POST handlers to Postgres.
  - Risk: Medium; Effort: M

## Admin
- Gap: branding uploads and users admin incomplete.
  - Files: admin/views.py, services/admin_service.py
  - Minimal fix: implement endpoints and storage adapter.
  - Risk: Medium; Effort: M

## Print Templates
- Gap: JSON endpoints not present.
  - Files: print_templates blueprint/service/repo
  - Minimal fix: add blueprint with service/repo; maintain legacy paths.
  - Risk: Low; Effort: M

