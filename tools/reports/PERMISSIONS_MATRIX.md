# Permissions Matrix

Roles: Admin, FrontDesk, Prep, Sprayer, QA, Manager, Customer

| Route/Action | Admin | FrontDesk | Prep | Sprayer | QA | Manager | Customer |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /login (GET/POST) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| /logout | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| /customers (view) | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| /customers/<id> (view) | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| /customers (create/edit) | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| /jobs (view) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| /jobs/<id>/edit | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| /jobs/photos upload/delete | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| /powders (view) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| /powders (create/edit) | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| /inventory (view) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| /inventory update/adjust | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| /sprayer batches/actions | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |
| /customer/* (portal) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| /admin/* (branding/users/config) | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| /api/print-templates* | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |

Notes:
- Align with legacy behaviors; adjust per real checks in code during implementation.

