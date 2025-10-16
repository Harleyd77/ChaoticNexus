# Industrial Forge Theme - Styling Guide

**Last Updated:** October 16, 2025

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

# Watch mode (auto-rebuild on save) - RECOMMENDED
cd /home/harley/chaoticnexus/app && npm run watch:servercss
```

---

## 🎨 Industrial Forge Theme Location

The Industrial Forge theme is defined in `app/src/app.tailwind.css`:

### Theme Variables (Lines ~192-217)
```css
html.theme-forge {
  --color-bg: #1a1614;
  --color-surface: #252220;
  --color-accent: #ff8c42;  /* Signature orange */
  --color-success: #4ade80;
  --color-text: #faf8f6;
  /* ... more variables */
}
```

### Theme Component Overrides (Lines ~504-615)

**This is where Forge gets its unique look!**

- **Primary Buttons**: Lines ~504-547
- **Secondary Buttons**: Lines ~549-582
- **Outline Buttons**: Lines ~584-595
- **Cards**: Lines ~597-614

---

## 🔘 Button Styling System

### Primary Buttons (Green/Emerald)

**HTML Classes Used:**
```html
<button class="btn btn-primary">Save</button>
<a href="/somewhere" class="btn btn-primary">Link Button</a>
```

**Forge Theme Override (Lines ~504-547):**
```css
html.theme-forge .btn-primary {
  border-radius: 1.25rem !important;  /* Extra rounded */
  background: linear-gradient(to bottom, 
    #22c55e 0%,      /* Bright emerald at top */
    #16a34a 50%,     /* Mid emerald */
    #15803d 100%     /* Darker emerald at bottom */
  ) !important;
  box-shadow: 
    0 2px 0 rgba(255, 255, 255, 0.25) inset,
    0 -3px 0 rgba(0, 0, 0, 0.3) inset,
    0 6px 12px rgba(0, 0, 0, 0.5),
    0 3px 6px rgba(34, 197, 94, 0.6),
    0 1px 3px rgba(34, 197, 94, 0.8) !important;
  transform: translateY(0) scale(1);
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

**Key Features:**
- 3D metallic gradient (light to dark green)
- Multi-layer box shadows for depth
- Rounded corners (1.25rem = 20px)
- Green glow effect

**Hover State:**
```css
html.theme-forge .btn-primary:hover {
  background: linear-gradient(to bottom, 
    #4ade80 0%,      /* Brighter on hover */
    #22c55e 50%, 
    #16a34a 100%
  ) !important;
  transform: translateY(-4px) scale(1.02);  /* Lift effect */
  box-shadow: /* Enhanced shadows */ !important;
}
```

**Active/Press State:**
```css
html.theme-forge .btn-primary:active {
  background: linear-gradient(to bottom, 
    #166534 0%,      /* Darker when pressed */
    #15803d 50%, 
    #14532d 100%
  ) !important;
  transform: translateY(2px) scale(0.98);  /* Press down */
  box-shadow: /* Inset shadows */ !important;
}
```

### Secondary Buttons (Gray/Slate)

**HTML Classes Used:**
```html
<button class="btn btn-secondary">Cancel</button>
```

**Forge Theme Override (Lines ~549-582):**
```css
html.theme-forge .btn-secondary {
  border-radius: 1.25rem !important;
  background: linear-gradient(to bottom,
    rgba(71, 85, 105, 0.9) 0%,
    rgba(51, 65, 85, 0.9) 50%,
    rgba(30, 41, 59, 0.9) 100%
  ) !important;
  box-shadow: /* 3D effect with subtle orange glow */ !important;
  border: 1px solid rgba(255, 140, 66, 0.2) !important;
}
```

**Key Features:**
- Slate gray gradient
- Subtle orange glow/border (matching Forge accent)
- Same rounded corners as primary
- Slightly less prominent than primary

### Outline Buttons

**HTML Classes Used:**
```html
<button class="btn btn-outline">Details</button>
```

**Forge Theme Override (Lines ~584-595):**
```css
html.theme-forge .btn-outline {
  border-radius: 1.25rem !important;
  border: 1px solid rgba(255, 140, 66, 0.35) !important;  /* Orange border */
  color: rgba(255, 230, 204, 0.85) !important;
  box-shadow: 0 2px 0 rgba(255, 140, 66, 0.12) inset, 
              0 1px 3px rgba(255, 140, 66, 0.25) !important;
}

html.theme-forge .btn-outline:hover {
  background: rgba(255, 140, 66, 0.1) !important;  /* Light orange fill */
  border-color: rgba(255, 140, 66, 0.5) !important;
}
```

---

## 📦 Card Styling

**HTML Classes Used:**
```html
<div class="card">...</div>
<div class="card card-hover">...</div>  <!-- With hover effect -->
```

**Forge Theme Override (Lines ~597-614):**
```css
html.theme-forge .card {
  background: linear-gradient(135deg, 
    var(--color-card) 0%, 
    #2d2925 100%);
  border: 2px solid var(--color-border);
  border-radius: 1.5rem !important;  /* Even more rounded than buttons */
  box-shadow: 
    0 2px 0 rgba(255, 140, 66, 0.08) inset,
    0 4px 8px rgba(0, 0, 0, 0.3);
  transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
}

html.theme-forge .card-hover:hover {
  transform: translateY(-2px);  /* Lift on hover */
  box-shadow: 
    0 2px 0 rgba(255, 140, 66, 0.12) inset,
    0 0 24px rgba(255, 140, 66, 0.2),
    0 16px 36px rgba(255, 115, 32, 0.25);  /* Orange glow */
  border-color: rgba(255, 140, 66, 0.35);
}
```

**Key Features:**
- Diagonal gradient background
- Extra rounded (1.5rem = 24px)
- Orange glow on hover
- Lift animation

---

## 🎨 Design Philosophy

### Forge Theme Identity

**Industrial & Tactile:**
- 3D button effects simulate physical buttons
- Metallic gradients suggest metal finishing
- Orange accents reference heat/forge fire

**Rounded & Modern:**
- 1.25rem button radius (vs 0.5rem in Dark theme)
- 1.5rem card radius
- Smooth, friendly curves

**Depth & Shadows:**
- Multi-layer shadows create depth
- Inset highlights simulate 3D surface
- Hover states lift elements
- Active states press down

**Color Signature:**
- Primary actions: Emerald green gradients
- Accent/borders: Orange (#ff8c42)
- Background: Warm dark browns/grays
- Success states: Bright green glow

---

## 🔧 Customization Examples

### Make Buttons Even More Rounded

**Edit lines ~505, ~550, ~585:**
```css
html.theme-forge .btn-primary {
  border-radius: 1.5rem !important;  /* Changed from 1.25rem */
  /* ... */
}

html.theme-forge .btn-secondary {
  border-radius: 1.5rem !important;  /* Changed from 1.25rem */
  /* ... */
}

html.theme-forge .btn-outline {
  border-radius: 1.5rem !important;  /* Changed from 1.25rem */
  /* ... */
}
```

### Reduce Hover Lift Effect

**Edit line ~527:**
```css
html.theme-forge .btn-primary:hover {
  transform: translateY(-2px) scale(1.01);  /* Less dramatic */
  /* ... */
}
```

### Change Orange Accent to Red

**First, update the theme variable (line ~192):**
```css
html.theme-forge {
  --color-accent: #ff4242;  /* Red instead of orange */
  /* ... */
}
```

**Then update secondary button border (line ~561):**
```css
html.theme-forge .btn-secondary {
  border: 1px solid rgba(255, 66, 66, 0.2) !important;  /* Red */
  /* ... adjust shadows too */
}
```

**And outline button border (line ~586):**
```css
html.theme-forge .btn-outline {
  border: 1px solid rgba(255, 66, 66, 0.35) !important;
  /* ... */
}
```

### Remove 3D Effects (Make Flat Like Dark Theme)

**Edit lines ~504-547:**
```css
html.theme-forge .btn-primary {
  border-radius: 1.25rem !important;
  background: #16a34a !important;  /* Solid color, no gradient */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;  /* Simple shadow */
  transform: none !important;  /* No transforms */
  transition: all 150ms ease;
}

html.theme-forge .btn-primary:hover {
  background: #15803d !important;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.4) !important;
  transform: none !important;  /* No lift */
}

html.theme-forge .btn-primary:active {
  background: #14532d !important;
  transform: none !important;  /* No press */
}
```

---

## ⚙️ Development Workflow

### Step 1: Start Watch Mode
```bash
cd /home/harley/chaoticnexus/app
npm run watch:servercss
# Leave this terminal running
```

### Step 2: Edit CSS
Open `app/src/app.tailwind.css` in your editor

### Step 3: Make Changes
Find the Forge section (lines ~504-615) and edit

### Step 4: Save
Save the file (Ctrl+S)

### Step 5: Wait
Watch the terminal - you'll see "Rebuilding..." then "Done in XXXms"

### Step 6: Test
Hard refresh your browser (Ctrl+Shift+R) while on the Forge theme

### Step 7: Iterate
Repeat steps 3-6 until perfect!

---

## 🚨 Common Issues

### Changes Not Showing Up?

**Check 1: Did CSS build successfully?**
```bash
# Look in terminal for:
Done in XXXms  ✅ Good!

# Or errors like:
CssSyntaxError: ...  ❌ Fix the error first
```

**Check 2: Are you on the Forge theme?**
- Open browser DevTools (F12)
- Check `<html>` element
- Should have `class="theme-forge"`

**Check 3: Did you hard refresh?**
- Ctrl+Shift+R (Windows/Linux)
- Cmd+Shift+R (Mac)

**Check 4: Right file?**
- ✅ Edit: `app/src/app.tailwind.css`
- ❌ Don't edit: `app/static/css/app.css`

### Buttons Still Look Plain?

Make sure your HTML uses the right classes:
```html
✅ <button class="btn btn-primary">Good</button>
❌ <button class="button primary">Wrong</button>
❌ <button class="bg-green-500">Won't get Forge styling</button>
```

### Other Themes Look Broken After Forge Changes?

This shouldn't happen! Forge styles are isolated with `html.theme-forge` selector.

If it does happen:
- Check you didn't accidentally edit base classes (lines ~364-462)
- Check you didn't remove `html.theme-forge` from selectors
- Check you didn't add global styles outside the theme section

---

## 📏 Measurement Guide

### Border Radius Values
- `0.5rem` = 8px (subtle rounded - used in Dark theme)
- `0.75rem` = 12px (moderately rounded)
- `1rem` = 16px (rounded)
- `1.25rem` = 20px (extra rounded - **Forge buttons**)
- `1.5rem` = 24px (very rounded - **Forge cards**)

### Transform Values
- `translateY(-4px)` = lift 4 pixels on hover
- `translateY(2px)` = press down 2 pixels on click
- `scale(1.02)` = grow 2% on hover
- `scale(0.98)` = shrink 2% on click

### Shadow Layers
Forge uses multi-layer shadows for depth:
1. **Inset highlight** (top): Simulates light reflection
2. **Inset shadow** (bottom): Creates bevel edge
3. **Drop shadow**: Creates depth
4. **Glow shadows**: Colored effects (green/orange)

---

## 🎯 Quick Tweaks Cheat Sheet

| Want to... | Edit This |
|-----------|-----------|
| Change button roundness | `border-radius` values on lines ~505, ~550, ~585 |
| Change card roundness | `border-radius` on line ~600 |
| Adjust hover lift | `translateY` value on line ~527 |
| Change button colors | Gradient colors on lines ~506-509 |
| Adjust orange glow | `rgba(255, 140, 66, ...)` values throughout |
| Remove 3D effect | Replace gradients with solid colors, remove transforms |
| Change shadow intensity | Adjust `box-shadow` values throughout |
| Speed up animations | Change `transition` duration (line ~518) |

---

## 📚 Related Documentation

- **Overall Theme System**: `/home/harley/chaoticnexus/UNIFIED_THEME_SYSTEM.md`
- **Project Standards**: `/home/harley/chaoticnexus/PROJECT_STANDARDS.md`
- **CSS Source File**: `/home/harley/chaoticnexus/app/src/app.tailwind.css`

---

## 💡 Pro Tip

**Want to copy Forge's 3D style to another theme?**

1. Copy the entire Forge section (lines ~504-615)
2. Paste it at the end of the file
3. Find/replace `theme-forge` with `theme-yourtheme`
4. Adjust colors to match your theme's palette
5. Rebuild and test!

**Example:**
```bash
# In your editor:
# Copy lines 504-615
# Paste at line 1200
# Find: html.theme-forge
# Replace with: html.theme-ocean
# Then adjust green colors to cyan/blue
```

---

**Last Updated:** October 16, 2025  
**Forge Theme Lines:** ~504-615 in `app/src/app.tailwind.css`
