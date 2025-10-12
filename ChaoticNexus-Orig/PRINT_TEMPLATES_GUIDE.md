# Print Templates System Guide

## Overview

Your PowderApp now has a **server-side print templates system** that allows you to:
- Save custom print layouts for each type of intake form
- Templates are stored in the database (not browser localStorage)
- Each form type can have its own template
- Templates automatically apply when you open or print a form
- Edit templates occasionally through the admin interface

## How It Works

### 1. **Customize a Layout**

When viewing a job worksheet:
1. Click the **Layout customization button** (grid icon, top right)
2. **Customize Layout mode** will activate
3. You can now:
   - **Drag fields** to reorder them
   - **Click field labels** to rename them
   - **Resize fields** by dragging the corner handles

### 2. **Save Your Template**

Once you're happy with the layout:
1. Click the **"Save Layout"** button in the controls panel
2. Your template is saved to the database
3. This template will now be used for ALL job worksheets going forward

### 3. **Print Preview**

Before printing:
1. Click the **Print Preview button** (printer icon)
2. See exactly how the form will look when printed
3. Make any final adjustments
4. Click the **Print button** to print

### 4. **Manage Templates (Admin)**

Access the template management page:
1. Go to **Admin Panel** (`/admin`)
2. Click **"Manage Print Templates"**
3. You'll see templates for:
   - **Job Worksheets** - Work order forms
   - **Intake Forms** - Regular production intake
   - **Railing Intake Forms** - Railing-specific intake

For each template type you can:
- **View all saved templates**
- **Set which template is the default**
- **Delete old templates**
- **See when templates were created/updated**

## Template Types

The system supports separate templates per workflow. Job worksheets now have distinct templates depending on whether the job came from the production intake or the railing intake. Current template types are:

| Type | Description | Where It's Used |
|------|-------------|----------------|
| `job_worksheet_production` | Job worksheets for production intake jobs | `/job-workorder/<job_id>` |
| `job_worksheet_railing` | Job worksheets for railing intake jobs | `/job-workorder/<job_id>` |
| `intake_form` | Regular production intake | `/intake_form` |
| `railing_intake` | Railing-specific intake | `/railing_intake` |

## Key Features

### ✅ Persistent Templates
- Templates are saved in the database
- They work across all devices and browsers
- No more losing your layout when clearing browser data

### ✅ Per-Form-Type Templates
- Each form type can have its own layout
- Job worksheets can look different from intake forms
- Set once, use everywhere

### ✅ Default Template System
- Mark one template as "default" for each form type
- Default templates automatically apply to new forms
- Easy to switch defaults in the admin panel

### ✅ Easy Management
- Admin interface shows all templates
- See creation dates and who created them
- Delete old templates you no longer need

## Workflow Examples

### Example 1: Setting Up Job Worksheet Template
1. Open any job worksheet for the intake source you want to change (production intake jobs load `job_worksheet_production`, railing intake jobs load `job_worksheet_railing`).
2. Click the grid icon (Layout Customize)
3. Rearrange fields as needed (e.g., move "Customer" to the top)
4. Resize the "Notes" field to be larger
5. Rename "Tank /" to "Tank Type"
6. Click **"Save Layout"**
7. Done! This layout will now be used for all job worksheets

### Example 2: Changing the Default Template
1. Go to Admin Panel: `/admin`
2. Click **"Manage Print Templates"**
3. Find the template you want to use
4. Click **"Set as Default"**
5. Confirm the change
6. That template is now the default for that form type

### Example 3: Resetting to Default Layout
1. Open the form
2. Click the Layout Customize button
3. Click **"Reset to Default"**
4. Confirm - this will reload the default layout

## Technical Details

### API Endpoints

The system provides these REST API endpoints:

- `GET /api/print-templates/<template_type>` - Get default template for a type
- `GET /api/print-templates/<template_type>/all` - List all templates (admin only)
- `POST /api/print-templates` - Save a new template (admin only)
- `DELETE /api/print-templates/<id>` - Delete a template (admin only)
- `POST /api/print-templates/<id>/set-default` - Set as default (admin only)

### Database Schema

Templates are stored in the `print_templates` table:

```sql
CREATE TABLE print_templates (
    id SERIAL PRIMARY KEY,
    template_type TEXT NOT NULL,          -- 'job_worksheet_production', 'job_worksheet_railing', 'intake_form', 'railing_intake'
    template_name TEXT NOT NULL,          -- e.g., 'Default', 'Compact', 'Detailed'
    layout_json TEXT NOT NULL,            -- JSON of field layout
    is_default INTEGER DEFAULT 0,         -- 1 if this is the default template
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_by TEXT,                      -- Username who created it
    UNIQUE(template_type, template_name)
);
```

## Troubleshooting

### Problem: Layout not saving
**Solution**: Make sure you're logged in as an admin. Only admins can save templates.

### Problem: Old localStorage layout still showing
**Solution**: The system now uses server-side templates. Old localStorage data is ignored. If you want to keep an old layout, recreate it and save it as a new template.

### Problem: Layout looks different when printing
**Solution**: Use the Print Preview button first to see exactly how it will print. Make adjustments in layout mode, then save.

### Problem: Can't delete a template
**Solution**: Make sure you're logged in as an admin. Templates can only be managed by administrators.

## Migration from Old System

If you were using the old localStorage-based system:

1. **Your old layouts are still in browser localStorage** (but won't be used anymore)
2. **To convert**: 
   - Open the form
   - Click Layout Customize
   - The default layout will load
   - Recreate your preferred layout
   - Click "Save Layout" to save it to the database

## Best Practices

1. **Name your templates descriptively** - Use names like "Detailed Layout" or "Compact Print"
2. **Test before setting as default** - Preview templates before making them the default
3. **Keep backups** - Don't delete old templates immediately, keep them for a while
4. **Document changes** - Note why you changed a template in your internal docs
5. **Regular reviews** - Periodically review and clean up unused templates

## Support

If you encounter issues:
1. Check the browser console for error messages
2. Verify you're logged in as an admin
3. Check that the database table `print_templates` exists
4. Contact your system administrator

---

**Created**: October 2025  
**Version**: 1.0  
**For**: PowderApp 1.3




