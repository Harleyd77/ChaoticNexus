# Legacy Template Migration Checklist

Progress tracker for porting legacy ChaoticNexus-Orig templates into the modern Flask/Tailwind stack. Mark each item once the template has been migrated, styled to project standards, and verified in the app.

## Foundation
- [x] Base layout scaffold (`app/templates/_layouts/base.html`)
- [x] Navigation shell (`nav.html`)
- [x] Error template (`error.html`)

## Jobs Suite
- [x] Jobs index (`jobs.html`)
- [x] Jobs kanban (`jobs_kanban.html`)
- [x] Job view (`job_view.html`)
- [x] Job edit (`job_edit.html`)
- [ ] Work order (`job_workorder.html`)

## Powders & Inventory
- [ ] Powders index (`powders.html`)
- [ ] Powder edit (`powder_edit.html`)
- [ ] Powder form fields partial (`_powder_form_fields.html`)
- [ ] Reorder list (`reorder_list.html`)
- [ ] Inventory overview (`inventory.html`)
- [ ] Inventory history (`inventory_history.html`)

## Sprayer & Production
- [ ] Sprayer batches (`sprayer_batches.html`)
- [ ] Sprayer batch detail (`sprayer_batch.html`)

## Intake & Measurement Forms
- [ ] Intake form (`intake_form.html`)
- [ ] Railing intake (`RailingIntake.html`)
- [ ] Measurement form (`MeasurementForm(Railings).html`)

## Admin & Print
- [ ] Admin users (`admin_users.html`)
- [ ] Print templates admin (`print_templates_admin.html`)

## React Bridge / Transitional Views
- [ ] React app host (`react_app.html`)
- [ ] React demo (`react_demo.html`)

## Archive / Cleanup
- [ ] Intake form backup (`intake_form.backup.html`)
- [ ] Intake form test (`intake_form.test.html`)
- [ ] Legacy nav backup (`nav-20251007_202632.backup.html`)
- [ ] Legacy static dist landing (`static/dist/index.html`)
