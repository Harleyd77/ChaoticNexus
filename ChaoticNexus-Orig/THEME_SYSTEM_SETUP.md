# 🎨 Unified Theme System - Setup Guide

## What You Get

A **consistent, floating theme button** appears on every page in the top-right corner, offering 6 beautiful themes:
- 🌙 **Dark** (default dark blue/gray)
- ☀️ **Light** (clean white)
- 🔷 **VPC Dark** (cobalt/steel dark)
- 💎 **VPC Light** (cobalt on light)
- ⚡ **Chaotic Dark** (electric purple/magenta)
- ✨ **Chaotic Light** (purple on warm gray)

Themes persist across pages via `localStorage` and apply instantly!

---

## How to Add to ANY Page

### Step 1: Add CSS to `<head>`

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/theme.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
```

### Step 2: Add JS before `</head>` or `</body>`

```html
<script src="{{ url_for('static', filename='js/theme.js') }}"></script>
<script src="{{ url_for('static', filename='js/motion.js') }}"></script>
<script src="{{ url_for('static', filename='js/ui-core.js') }}"></script>
<script src="{{ url_for('static', filename='js/global-theme-menu.js') }}"></script>
```

### That's It! ✨

The theme button will automatically appear in a **fixed position at the top-right** (below the dev banner).

---

## Full Example Template

```html
<!doctype html>
<html lang="en" data-theme="{{ request.cookies.get('vpc_theme', 'dark') }}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>My Page · VPC</title>
  
  <!-- Your existing CSS -->
  <style>
    /* Your custom styles here */
  </style>
  
  <!-- Unified theme system -->
  <link rel="stylesheet" href="{{ url_for('static', filename='css/theme.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
  <script src="{{ url_for('static', filename='js/theme.js') }}"></script>
  <script src="{{ url_for('static', filename='js/motion.js') }}"></script>
  <script src="{{ url_for('static', filename='js/ui-core.js') }}"></script>
  <script src="{{ url_for('static', filename='js/global-theme-menu.js') }}"></script>
</head>
<body>
  <!-- Theme button automatically appears here -->
  
  <!-- Your page content -->
  <h1>My Page</h1>
  
</body>
</html>
```

---

## Using Theme Variables in Your CSS

Replace hardcoded colors with theme variables:

### Before:
```css
.my-element {
  background: #111827;
  color: #e6edf3;
  border: 1px solid #1f2a37;
}
```

### After:
```css
.my-element {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}
```

### Available Variables:

#### Colors
- `--color-bg` - Page background
- `--color-surface` - Card/panel background
- `--color-surface-muted` - Alternate surface
- `--color-border` - Border color
- `--color-text` - Primary text
- `--color-text-muted` - Secondary text
- `--color-accent` - Primary button/link color
- `--color-accent-strong` - Hover/active accent
- `--color-success` - Success states (#22C55E)
- `--color-warning` - Warning states (#F59E0B)
- `--color-danger` - Error states (#EF4444)
- `--color-info` - Info states (#38BDF8)

#### Borders & Shadows
- `--radius-sm` - Small radius (0.375rem)
- `--radius-md` - Medium radius (0.5rem)
- `--radius-lg` - Large radius (0.75rem)
- `--radius-xl` - Extra large radius (1rem)
- `--shadow-sm` - Small shadow
- `--shadow-md` - Medium shadow
- `--shadow-lg` - Large shadow

---

## Pages Already Updated

✅ `/nav` - Navigation page  
✅ `/customers` - Customer list  
✅ `/jobs` - Job database  

## Pages That Need Updating

- `/powders` - Powder inventory
- `/admin` - Admin panel
- `/railing_intake` - Railing intake form
- `/intake_form` - Production intake
- `/sprayer/*` - Sprayer pages (batches, hit list)
- Any other custom pages

Just add the 6 lines (2 CSS + 4 JS) to each page's `<head>` section!

---

## Troubleshooting

### Theme button not showing?
1. Check browser console for errors
2. Hard refresh (`Ctrl+Shift+R`)
3. Verify all 6 files are loading (check Network tab)

### Theme not persisting?
- The theme is saved to `localStorage['theme']`
- Check if browser allows localStorage

### Theme not changing colors?
- Make sure your CSS uses `var(--color-*)` variables
- Old hardcoded colors won't change automatically

---

## Theme Button Position

The button appears **fixed at top-right: `top: 72px, right: 20px`**

To adjust position, edit `/static/js/global-theme-menu.js` line 24:
```javascript
menu.style.cssText = 'position: fixed; top: 72px; right: 20px; z-index: 9999;';
```

---

**Created**: October 4, 2025  
**Version**: 1.0

