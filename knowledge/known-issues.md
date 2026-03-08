# LoveSpark Known Issues Registry

Read this BEFORE any UI work. Every entry represents a mistake that was made, debugged, and fixed. Do not repeat them.

---

## KI-001: White text on --ls-pink-accent fails contrast in ALL themes

**Category:** Contrast
**Severity:** Critical
**First found:** cozy-accessibility build (2026-03)
**Themes affected:** ALL (retro 3.77:1, dark 2.58:1, beige 3.16:1, slate 3.35:1)

**Symptom:** White text on `--ls-pink-accent` buttons is hard to read
**Root cause:** `--ls-pink-accent` is designed as a decorative/highlight color, not a text-background pair. Too luminous for white text.
**Fix:** Use `--ls-btn-hover-bg` for button backgrounds that need white text. It passes 4.5:1 in all themes.
**Prevention rule:** NEVER use `--ls-pink-accent` as background for white text. Use `--ls-btn-hover-bg` instead. If you need pink buttons with white text, always use `--ls-btn-hover-bg`.

---

## KI-002: Slate muted text on glass-strong fails 4.5:1

**Category:** Contrast
**Severity:** High
**First found:** audit-contrast.py (2026-03)
**Themes affected:** Slate only (4.17:1, needs 4.5:1)

**Symptom:** `--ls-text-muted` (#9A9A9A) on `--ls-glass-strong` (#383838) in slate theme is borderline unreadable
**Root cause:** Slate muted text and glass-strong are too close in luminance
**Fix:** Either lighten slate `--ls-text-muted` to ~#ABABAB or darken `--ls-glass-strong` to ~#333333
**Prevention rule:** After adding or modifying any theme token, run `audit-contrast.py --theme [name]` immediately.

---

## KI-003: Slate slider thumb on glass-border fails 3:1

**Category:** Contrast (UI component)
**Severity:** Medium
**First found:** audit-contrast.py (2026-03)
**Themes affected:** Slate only (2.65:1, needs 3:1)

**Symptom:** Slider thumb (`--ls-focus-ring` #D4714E) against track (`--ls-glass-border` #4A4A4A) in slate lacks sufficient contrast
**Root cause:** Focus ring and glass border are too close in luminance in slate
**Fix:** Lighten slate `--ls-focus-ring` slightly or darken `--ls-glass-border`
**Prevention rule:** Always check focus-ring vs glass-border contrast for UI component 3:1 requirement.

---

## KI-004: Beige hint text at 0.8 opacity fails 4.5:1

**Category:** Contrast
**Severity:** Medium
**First found:** audit-contrast.py (2026-03)
**Themes affected:** Beige only (4.26:1, needs 4.5:1)

**Symptom:** Text with `opacity: 0.8` on beige glass drops below threshold
**Root cause:** Opacity reduces effective contrast. Beige has lower base contrast than retro.
**Fix:** Either increase opacity to 0.85+ on beige, or use full-opacity `--ls-text-muted` instead of opacity-reduced `--ls-text-dark`
**Prevention rule:** Never use opacity < 0.85 on text in beige theme. Prefer `--ls-text-muted` over opacity hacks.

---

## KI-005: Missing ARIA on popup containers

**Category:** ARIA
**Severity:** Critical
**First found:** cozy-accessibility review round 2 (2026-03)

**Symptom:** Screen readers don't announce popup purpose
**Root cause:** Popup containers missing `role="alertdialog"`, `aria-labelledby`, `aria-describedby`
**Fix:** Add all three attributes to the main popup container div
**Prevention rule:** EVERY popup.html must have `role="alertdialog"` on its container. Use the canonical popup shell from accessibility-framework.md.

---

## KI-006: Focus indicators invisible or missing

**Category:** Keyboard/Focus
**Severity:** Critical
**First found:** cozy-accessibility review round 3 (2026-03)

**Symptom:** Keyboard users can't see which element is focused
**Root cause:** No `:focus-visible` styles, or browser default outline suppressed
**Fix:** Add `:focus-visible { outline: 2px solid var(--ls-focus-ring); outline-offset: 2px; }` on ALL interactive elements
**Prevention rule:** Every CSS file must have `:focus-visible` rules for buttons, inputs, toggles, tabs, links, selects. Search for `focus-visible` in CSS before marking any UI done.

---

## KI-007: Touch targets under 32px

**Category:** Touch/Layout
**Severity:** High
**First found:** cozy-accessibility review round 4 (2026-03)

**Symptom:** Small buttons and toggles are hard to tap on mobile
**Root cause:** Missing `min-height` on interactive elements
**Fix:** Add `min-height: 32px` to all buttons, toggles, tabs, and links
**Prevention rule:** Every interactive CSS selector must include `min-height: 32px`. Grep for button/toggle/tab selectors and verify.

---

## KI-008: Missing prefers-reduced-motion

**Category:** Motion
**Severity:** High
**First found:** cozy-accessibility review round 1 (2026-03)

**Symptom:** Animations play for users who need reduced motion
**Root cause:** CSS has `transition` and `animation` but no `prefers-reduced-motion` media query
**Fix:** Add the canonical reduced-motion block (see accessibility-framework.md Section 7)
**Prevention rule:** If a CSS file contains ANY `transition` or `animation` property, it MUST also contain a `@media (prefers-reduced-motion: reduce)` block.

---

## KI-009: Theme title color overrides missing

**Category:** Contrast
**Severity:** Medium
**First found:** First beige/slate theme implementation (2025)

**Symptom:** Title text unreadable on beige (pink on cream) and slate (pink on dark gray)
**Root cause:** Default `--ls-text-dark` title color doesn't work on beige/slate
**Fix:** Add `.theme-beige .header-title { color: #3d5a2e; }` and `.theme-slate .header-title { color: #e8926e; }`
**Prevention rule:** After adding title text, verify it's readable in ALL 4 themes. Beige and slate need explicit overrides.

---

## KI-010: Beige text-muted value discrepancy between base.css and extensions

**Category:** Consistency
**Severity:** Medium
**First found:** accessibility toolkit build (2026-03)

**Symptom:** `--ls-text-muted` is #8b6f47 in canonical base.css but #6b5630 in cozy-accessibility
**Root cause:** cozy-accessibility refined the value for better contrast but didn't update canonical source
**Fix:** Determine which value passes all checks, update canonical `lovespark-base.css`, then run `sync-shared-lib.sh`
**Prevention rule:** Token values must ONLY be changed in canonical `lovespark-base.css`. After changing, run `sync-shared-lib.sh` and `audit-contrast.py`.

---

## Adding New Issues

When you encounter a new issue during a build or review:

1. Assign the next KI number (KI-011, etc.)
2. Fill in all fields: Category, Severity, First found, Symptom, Root cause, Fix, Prevention rule
3. The prevention rule must be actionable and specific — not "be careful"
4. If the issue should also update `debugging.md`, add it there too
5. If the issue reveals a tool gap, add it to `tool-changelog.md`
