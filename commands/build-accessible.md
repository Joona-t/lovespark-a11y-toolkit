Guide building an accessible LoveSpark UI from scratch. Load the accessibility framework first, then follow each step.

## Step 0: Load Framework + Memory (MANDATORY)

Read these files before writing ANY code:

1. `~/.claude/docs/accessibility-framework.md` — single source of truth for accessibility
2. `~/.claude/docs/memory/known-issues.md` — every past mistake with prevention rules
3. `~/.claude/docs/memory/color-decisions.md` — safe and dangerous color pairings
4. `~/.claude/docs/brand.md` and `~/.claude/docs/components.md` — brand/component context

Review every KI prevention rule in known-issues.md. These are mistakes we've already made and must not repeat.

## Step 1: Plan Component Tree

Before writing any code, list all interactive elements the UI will contain:

- For each element, assign its ARIA role (tab, tabpanel, button, checkbox, slider, menu, menuitem, alertdialog, etc.)
- Define the keyboard interaction model (which keys do what)
- Identify which elements need `aria-label`, `aria-expanded`, `aria-live`, `aria-controls`, `aria-selected`
- Map focus order (Tab sequence)
- Note which elements have dynamic content that needs `aria-live`

Present this as a table for review before proceeding.

## Step 2: Write HTML

Use canonical component patterns from the accessibility framework (Section 4):

- **Popup shell:** `role="alertdialog"`, `aria-labelledby`, `aria-describedby`, `lang="en"`
- **Toggles:** Hidden checkbox pattern with `aria-label`, `:focus-visible` on track
- **Tabs:** Roving tabindex, `role="tablist/tab/tabpanel"`, `aria-selected`, `aria-controls`
- **Dropdowns:** `aria-expanded`, `aria-haspopup`, `role="menu"`, `role="menuitem"`
- **Sliders:** `aria-labelledby`, `aria-valuenow`, `aria-valuetext`
- **Stats:** `aria-live="polite"` on dynamic values
- **Buttons:** Visible text or `aria-label`, never empty

Always include:
- Sparky mascot with `alt="Sparky -- LoveSpark mascot"` and explicit width/height
- Semantic elements: `<header>`, `<main>`, `<nav>`, `<section>`, `<footer>`
- `<html lang="en">`

## Step 3: Write CSS

Follow these hard rules from the framework:

**Colors — ONLY use pre-verified tokens:**
- Body text: `var(--ls-text-dark)`
- Secondary text: `var(--ls-text-muted)`
- Button hover bg: `var(--ls-btn-hover-bg)` with white text
- Focus indicators: `var(--ls-focus-ring)`
- NEVER hardcode hex colors for text or backgrounds

**Focus styles — required on ALL interactive elements:**
```css
.element:focus-visible {
  outline: 2px solid var(--ls-focus-ring);
  outline-offset: 2px;
}
```

**Touch targets:**
- All interactive elements: `min-height: 32px`
- Minimum 8px gap between adjacent interactive elements

**Motion — include this block in every CSS file with animations:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Layout:**
- Popup width: 320-360px
- Z-index: content auto, headers 10, dropdowns 100, modals 200
- Body overflow: scroll content area, never clip

## Step 4: Write JS

Include keyboard navigation for all interactive patterns:

**Tabs (roving tabindex):**
- ArrowLeft/Right to switch tabs
- Home/End for first/last
- Update `tabindex` and `aria-selected` on switch

**Dropdowns:**
- Enter/Space to open
- ArrowDown/Up to navigate
- Escape to close and return focus to trigger
- Update `aria-expanded` on toggle

**Toggles:**
- Space/Enter to toggle (native checkbox handles this)

**Sliders:**
- Update `aria-valuenow` and `aria-valuetext` on change
- Update visible value label

**Dynamic content:**
- Update `aria-live` regions when values change (the browser announces changes automatically)

## Step 5: Verify

Run the accessibility audit with history tracking:

```
python3 "/Users/darkfire/Claude x LoveSpark/scripts/audit-contrast.py" --verbose --history
```

Then walk through the checklist from the framework (Section 9):

1. Keyboard: Tab through all controls, Escape closes dropdowns, arrows work in tabs/menus
2. Screen reader: All elements have labels, dynamic content uses aria-live
3. Visual: Check all 4 themes for readability
4. Motion: Verify reduced-motion block covers all animations
5. Touch: All targets >= 32px

## Step 6: Postmortem

After completing the build, run `/postmortem` to capture what was learned. This updates the knowledge base so future builds benefit from this session's experience.

## Hard Rules Reminder

**NEVER:**
- Color as only state indicator
- Suppress outline without replacement
- Touch targets < 32px
- Skip prefers-reduced-motion
- Use --ls-text-white for body text
- Hardcode hex colors
- Empty buttons or links
- tabindex > 0

**ALWAYS:**
- --ls-focus-ring for focus indicators
- --ls-text-dark for body text
- role="alertdialog" on popup containers
- aria-label on icon-only controls
- aria-expanded on toggle triggers
- aria-live on dynamic content
- Test keyboard-only before marking done
