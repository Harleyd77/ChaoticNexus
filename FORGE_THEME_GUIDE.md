# Industrial Forge Theme - Styling Guide

**Last Updated:** October 15, 2025

## 📍 Quick Reference

### Files to Edit
- **Theme CSS Source**: `app/src/app.tailwind.css`
- **Compiled Output**: `app/static/css/app.css` (auto-generated, don't edit directly)
- **Button Macros**: `app/templates/_macros/ui.html`
- **Theme JavaScript**: `app/static/js/theme.js`

### Build Commands
```bash
# One-time build
cd /home/harley/chaoticnexus/app && npm run build:servercss

# Watch mode (auto-rebuild on save)
cd /home/harley/chaoticnexus/app && npm run watch:servercss
```

---

## 🎨 Industrial Forge Theme Location

The Industrial Forge theme is defined in `app/src/app.tailwind.css`:

### Theme Variables (Lines 192-217)
```css
html.theme-forge {
  --color-bg: #1a1614;
  --color-surface: #252220;
  --color-accent: #ff8c42;  /* Signature orange */
  /* ... more variables */
}
```

### Component Enhancements (Lines 448-578)
- **Cards**: Lines 448-468
- **Primary Buttons**: Lines 470-531
- **Secondary Buttons**: Lines 533-585

---

## 🔘 Button Styling System

### Primary Buttons (Green/Emerald)

**HTML Classes Used:**
```html
<!-- From app/templates/_macros/ui.html -->
<a class="inline-flex items-center ... bg-emerald-500 ...">
<button class="inline-flex items-center ... bg-emerald-500 ...">
```

**CSS Selector Pattern:**
```css
html.theme-forge button.bg-emerald-500,
html.theme-forge a.bg-emerald-500 {
  border-radius: 1.25rem !important;  /* 20px - adjust for roundness */
  background: linear-gradient(...);    /* 3-color gradient for depth */
  box-shadow: ...;                     /* Multi-layer shadows */
}
```

**Key Properties to Adjust:**
- `border-radius`: Controls roundness (current: 1.25rem / 20px)
- `background`: Gradient colors for metallic effect
- `box-shadow`: Stacked shadows for 3D depth
- `transform`: translateY for lift/press effects

### Secondary Buttons (Gray/Slate)

**HTML Classes Used:**
```html
<a class="inline-flex items-center ... bg-slate-800/70 ...">
<button class="inline-flex items-center ... bg-slate-800/70 ...">
```

**CSS Selector Pattern:**
```css
html.theme-forge button.bg-slate-800,
html.theme-forge a.bg-slate-800 {
  border-radius: 1.25rem !important;
  background: linear-gradient(...);
  box-shadow: 
    ...,
    0 1px 3px rgba(255, 140, 66, 0.25);  /* Orange forge glow */
}
```

---

## 🎯 Common Modifications

### Make Buttons More/Less Rounded
```css
/* More rounded (pillowy) */
border-radius: 1.5rem !important;  /* 24px */

/* Less rounded (subtle) */
border-radius: 0.75rem !important;  /* 12px */

/* Completely square */
border-radius: 0 !important;
```

### Adjust 3D Depth
```css
/* Hover state - lift amount */
transform: translateY(-4px) scale(1.02);  /* Current: -4px lift */
transform: translateY(-6px) scale(1.03);  /* More dramatic */
transform: translateY(-2px) scale(1.01);  /* Subtle */

/* Active state - press amount */
transform: translateY(2px) scale(0.98);   /* Current: 2px press */
```

### Change Shadow Intensity
```css
/* Default shadow stack */
box-shadow: 
  0 2px 0 rgba(255, 255, 255, 0.25) inset,  /* Top highlight */
  0 -3px 0 rgba(0, 0, 0, 0.3) inset,         /* Bottom shadow */
  0 6px 12px rgba(0, 0, 0, 0.5),             /* Drop shadow */
  0 3px 6px rgba(34, 197, 94, 0.6),          /* Colored glow */
  0 1px 3px rgba(34, 197, 94, 0.8);          /* Tight glow */

/* More subtle */
box-shadow: 
  0 1px 0 rgba(255, 255, 255, 0.15) inset,
  0 -2px 0 rgba(0, 0, 0, 0.2) inset,
  0 4px 8px rgba(0, 0, 0, 0.3),
  0 2px 4px rgba(34, 197, 94, 0.4);
```

### Modify Button Colors
```css
/* Primary button gradient */
background: linear-gradient(to bottom, 
  #22c55e 0%,   /* Top - brightest */
  #16a34a 50%,  /* Middle */
  #15803d 100%  /* Bottom - darkest */
);

/* Change to blue tones */
background: linear-gradient(to bottom, 
  #3b82f6 0%,
  #2563eb 50%,
  #1d4ed8 100%
);
```

---

## 📦 Cards Styling

**CSS Location:** Lines 448-468

```css
html.theme-forge .card {
  border-radius: 1.5rem !important;  /* Card roundness */
  background: linear-gradient(135deg, var(--color-card) 0%, #2d2925 100%);
  border-width: 2px;
  box-shadow: ...;
}
```

**Hover Effect:**
```css
html.theme-forge .card-hover:hover {
  transform: translateY(-2px);  /* Lift on hover */
  box-shadow: ...;              /* Enhanced glow */
}
```

---

## 🔧 Development Workflow

### Making Changes

1. **Edit the source file:**
   ```bash
   nano app/src/app.tailwind.css
   # or use your preferred editor
   ```

2. **If watch mode is running:** Changes compile automatically
3. **If not, manually build:**
   ```bash
   cd /home/harley/chaoticnexus/app && npm run build:servercss
   ```

4. **Hard refresh browser:** `Ctrl+Shift+R` (Linux/Windows) or `Cmd+Shift+R` (Mac)

### Testing Changes

1. Switch to Industrial Forge theme in the theme picker
2. Test hover states on buttons
3. Test click/press states
4. Check on different pages (dashboard, forms, etc.)

---

## 🎨 Theme Color Palette

```css
Background:     #1a1614
Surface:        #252220
Border:         #3a3331
Text:           #faf8f6
Accent:         #ff8c42  /* Signature forge orange */
Success/Green:  #4ade80
Warning:        #fbbf24
Danger:         #f87171
```

---

## ⚠️ Important Notes

### CSS Specificity
Always use `!important` on `border-radius` for theme overrides:
```css
border-radius: 1.25rem !important;
```

### Selector Matching
Match the actual HTML classes from `app/templates/_macros/ui.html`:
- ✅ `button.bg-emerald-500` matches `<button class="... bg-emerald-500 ...">`
- ❌ `button.inline-flex.bg-emerald-500` is too specific and may not match
- ✅ `a.bg-emerald-500` matches link buttons
- ✅ Use `,` to apply to both `button` and `a` tags

### Don't Edit Compiled CSS
Never edit `app/static/css/app.css` directly - it gets overwritten by the build process!

---

## 🔍 Quick Troubleshooting

**Changes not showing up?**
1. Check if watch mode is running
2. Force rebuild: `npm run build:servercss`
3. Hard refresh browser (clear cache)
4. Verify you're editing `app/src/app.tailwind.css` not `app/static/css/app.css`

**Buttons still square?**
1. Check CSS selector matches HTML classes
2. Verify `!important` is used on border-radius
3. Check browser DevTools to see which styles are applied

**3D effects not working?**
1. Verify all box-shadow layers are present
2. Check transform properties are included
3. Ensure transition is defined for smooth animations

---

## 📚 Related Documentation

- **Theme System Overview**: `ChaoticNexus-Orig/THEME_SYSTEM_VERIFICATION.md`
- **Styling Refactor Report**: `ChaoticNexus-Orig/STYLING_REFACTOR_REPORT.md`
- **Tailwind Config**: `app/tailwind.config.js`
- **Button Macros**: `app/templates/_macros/ui.html`

---

## 💡 Tips & Tricks

1. **Use CSS Variables** where possible for consistency:
   ```css
   background: var(--color-accent);
   ```

2. **Stack shadows** for depth (not just one shadow):
   ```css
   box-shadow: 
     /* inset highlight */,
     /* inset shadow */,
     /* drop shadow */,
     /* glow */;
   ```

3. **3-color gradients** look more metallic than 2-color:
   ```css
   linear-gradient(to bottom, bright 0%, mid 50%, dark 100%)
   ```

4. **Always include hover AND active states** for polish:
   ```css
   html.theme-forge button:hover { }
   html.theme-forge button:active { }
   ```

---

**Questions or need to add more themes?**  
Follow the same pattern used for Industrial Forge in `app/src/app.tailwind.css`

