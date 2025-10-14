# Parity Matrix

Status: ✅ (parity), ⚠️ (partial), ❌ (missing)

| Area | Legacy Path(s) | New Target | Required Fields/Validation | Actions/Output | Status |
| --- | --- | --- | --- | --- | --- |
| Base | /, /nav, /favicon.ico, /uploads/<path> | /dashboard/, same | n/a | redirect 308, 200 favicon/uploads | ⚠️ |
| Auth | /login, /logout, /logout/customer | same | username/pin/password; CSRF | session create/destroy | ⚠️ |
| Customer Portal | /customer/* | same | register/forgot validators | list/detail/edit/submit | ⚠️ |
| Customers | /customers, JSON, contacts, admin accounts | same | required company/contact | CRUD + JSON | ⚠️ |
| Jobs | /jobs, kanban, detail/edit, photos, worksheet, CSV | same | job fields validation | status actions, CSV, uploads, delete | ⚠️ |
| Powders | /powders, edit/new/save/delete, CSV/API | same | powder fields | CSV import/export | ⚠️ |
| Inventory | /inventory, reorder, history, APIs | same | thresholds, updates | adjust/update/reorder | ⚠️ |
| Intake | /intake_form, /railing_intake, submit | /intake/* | required legacy fields | persist submission + file uploads | ✅ |
| Admin | /admin, branding, users, options, config | same | user/admin validators | branding uploads, perms | ⚠️ |
| Print Templates | /api/print-templates* | same | template type | list/create/delete/set-default | ❌ |

Notes:
- CSV endpoints remain; buttons hidden in UI per policy.
- No schema renames/changes; use service adapters and read-only views where needed.

