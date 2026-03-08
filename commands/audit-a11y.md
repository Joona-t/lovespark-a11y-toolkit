Perform a comprehensive accessibility audit on the current LoveSpark extension or UI project. The working directory should contain the extension's HTML, CSS, and JS files.

## Step 0: Load Memory (MANDATORY)

Before auditing, read the persistent knowledge base to check for known recurring issues:

1. Read `~/.claude/docs/memory/known-issues.md` — every KI entry is a mistake we've made before. Check if this project has any of them.
2. Read `~/.claude/docs/memory/color-decisions.md` — check if the project uses any "dangerous pairings" listed there.

Flag any known issues found immediately — these are RECURRENCES and must be fixed first.

## Step 0b: Dangerous Pairing Grep (MANDATORY)

Before even running the contrast tool, grep the project's CSS and JS for known dangerous pairings from color-decisions.md:

1. Grep CSS files for `--ls-pink-accent` used as `background` with white/light text — this is KI-001, fails in ALL themes
2. Grep CSS files for `opacity: 0.[0-7]` on text elements — KI-004 risk in beige theme
3. Grep JS files for both `storage.sync` and `storage.local` — KI-012, causes total feature failure
4. Grep JS files for `classList.toggle('open')` or `classList.add('open')` — check matching `setAttribute('aria-expanded')` exists (KI-013)
5. Grep HTML files for `<button` with emoji-only or symbol-only text (×, ▾, etc.) — verify `aria-label` present (KI-014)
6. Grep JS files for `.textContent =` — verify target element has `aria-live` attribute if it's a status/counter element. But NOT cosmetic rotating messages (KI-015 + KI-018)
7. Grep HTML files for `<input` and `<textarea` without `aria-label` or matching `<label>` — (KI-016)
8. Grep JS files for `innerHTML` — flag as XSS risk, must use `textContent` or DOM API (KI-011)
9. Grep background.js/service-worker.js for `setTimeout` — flag any that defer storage writes (KI-020)
10. Grep background.js/service-worker.js for `catch` with empty body `{}` — must log errors (KI-021)
11. Grep JS files for `onRuleMatchedDebug` used as if-guard — flag as packed extension bug (KI-019)
12. Grep CSS files for `outline: none` — verify every match has a corresponding `:focus-visible` with replacement outline (KI-006)

Flag any matches as KNOWN DANGEROUS PATTERNS before proceeding.

## Step 1: Contrast Audit

Run the automated contrast checker with history tracking:

```
python3 "/Users/darkfire/Claude x LoveSpark/scripts/audit-contrast.py" --verbose --history
```

Report results. If there are failures, list specific token fixes needed.

## Step 2: ARIA Audit

Search the project's HTML files for required ARIA patterns. Check for:

- `role="dialog"` on popup container with `aria-labelledby` (NOT `alertdialog` — that's for destructive confirm dialogs only)
- `aria-label` on every interactive element without visible text (buttons with only icons/emoji)
- `aria-expanded` on buttons that toggle dropdowns or panels
- `aria-haspopup` on dropdown triggers
- `role="tablist"`, `role="tab"`, `role="tabpanel"` on tab interfaces
- `aria-selected` on tab buttons
- `aria-controls` linking tabs to panels
- `aria-live="polite"` on elements with dynamic content (counters, status messages)
- `alt` text on all `<img>` tags (mascot should have `alt="Sparky -- LoveSpark mascot"`)
- No empty `<button>` or `<a>` tags (must have text content or aria-label)

Flag any missing patterns as FAIL.

## Step 3: Keyboard Navigation Audit

Search JS files for keyboard handling:

- `keydown` event listeners that handle `Escape`, `ArrowLeft`, `ArrowRight`, `ArrowUp`, `ArrowDown`, `Enter`, `Home`, `End`
- Roving tabindex pattern for tabs (`tabindex="0"` on active, `tabindex="-1"` on inactive)
- Focus return to trigger element when dropdowns/modals close
- No `tabindex` values > 0

Search CSS files for focus styles:

- `:focus-visible` rules on all interactive elements (buttons, inputs, toggles, links, tabs)
- Focus uses `var(--ls-focus-ring)` color
- `outline-offset` for clear visibility
- No `outline: none` without a replacement

## Step 4: Touch Target Audit

Search CSS for interactive element sizing:

- Check `height`, `min-height`, `padding` on buttons, toggles, tabs, links, inputs
- Flag any interactive element with computed height < 32px
- Check `gap` between adjacent interactive elements (minimum 8px)

## Step 5: Motion Audit

Search CSS for animation and motion handling:

- Check for `@media (prefers-reduced-motion: reduce)` block
- Verify it contains `animation-duration: 0.01ms !important` and `transition-duration: 0.01ms !important`
- Check for `animation` or `transition` properties in the CSS
- Flag any animation/transition NOT covered by the reduced-motion query

## Step 6: Screen Reader Audit

Check for screen reader compatibility:

- `lang="en"` on `<html>` element
- `aria-live` regions for dynamic content
- No `display: none` on elements that should be read (hidden inputs are OK)
- Semantic HTML usage (`<header>`, `<main>`, `<nav>`, `<section>`, `<footer>`)
- No duplicate IDs
- Form inputs have associated labels (via `<label>`, `aria-label`, or `aria-labelledby`)

## Step 7: Summary Report

Present a summary table:

| Category | Status | Issues |
|----------|--------|--------|
| Contrast | PASS/FAIL | [count] |
| ARIA | PASS/FAIL | [count] |
| Keyboard | PASS/FAIL | [count] |
| Touch Targets | PASS/FAIL | [count] |
| Motion | PASS/FAIL | [count] |
| Screen Reader | PASS/FAIL | [count] |

For each FAIL, list specific fixes with file paths and line numbers.

## Step 8: Update Knowledge Base

For any NEW issues found (not already in known-issues.md):
1. Suggest new KI entries with all required fields
2. Suggest tool improvements if the audit missed something it should have caught
3. Recommend running `/postmortem` to formally capture the learnings

For any RECURRING issues (already in known-issues.md):
1. Flag them as recurrences with the KI number
2. Suggest strengthening the prevention rule since it clearly didn't work
