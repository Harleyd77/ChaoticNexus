# Button System Roadmap

_Last updated: October 15, 2025_

This roadmap captures the plan for rolling out unified button utilities now and preparing for future design systems (e.g., shadcn/ui). It pairs with the architecture notes in `docs/project-overview.md` and the active tasks tracked in `docs/current-focus.md`.

---

## 1. Audit Current Usage
- Inventory all button-like elements across Flask templates, macros, and React components.
- Catalog Tailwind class patterns in use (`bg-emerald-500`, `bg-slate-800/70`, raw `<button>` tags).
- Record any exceptions (links acting as buttons, icon-only triggers, etc.).

## 2. Define Shared Button Utilities
- In `app/src/app.tailwind.css` under `@layer components`, add reusable classes:
  - `.btn` for shared base styles (`@apply inline-flex … transition disabled:*`).
  - `.btn-primary`, `.btn-secondary`, `.btn-ghost`, etc., using CSS variables for color/radius/shadow.
- Add a temporary fallback rule (`button:not([class*="btn"]) { @apply btn btn-secondary; }`) to catch legacy markup during the rollout.

## 3. Refactor Server-Side Macros
- Update `app/templates/_macros/ui.html` so macros emit `class="btn btn-primary"` (and variants) instead of hard-coded Tailwind strings.
- Sweep templates for inlined button markup and replace with macro calls or the new classes.

## 4. Align Client Components
- In the React/Vite code (`app/src/components`), expose a shared `Button` component that maps props to `btn-*` classes.
- Replace ad-hoc Tailwind button definitions with the shared component to ensure consistency across the SPA.

## 5. Hook Theme Overrides to New Classes
- Update each theme section in `app/src/app.tailwind.css` (Forge, Chaos, Ocean, etc.) to style `.btn-primary`, `.btn-secondary`, etc., instead of Tailwind utility selectors.
- Remove one-off selectors targeting specific `bg-*` classes once migration is complete.

## 6. Tokenize & Document
- Confirm button styles rely on theme CSS variables (colors, radii, shadows) defined in the theme blocks.
- Create a short guide (e.g., `docs/button-style-guide.md`) describing how to use the macros/classes and where to update tokens.

## 7. Gradual Migration Safety
- QA each page to confirm no legacy button styles remain; temporarily add alias selectors if necessary.
- Update PR checklist/lint rules to require `btn-*` classes or macros for new buttons.

## 8. Prepare for shadcn Adoption
- When introducing shadcn/ui, mirror the `btn-*` class API in shadcn components.
- Swap macro internals or React imports with shadcn equivalents, then retire fallback CSS once the transition is complete.

## 9. Testing & Verification
- After the refactor, sanity-check the appearance of primary/secondary buttons across all themes.
- Optional: add screenshot or Playwright smoke tests to ensure each variant renders correctly.

---

Following this roadmap keeps today’s UI consistent and makes future migrations (shadcn or other systems) low-risk and reversible.
