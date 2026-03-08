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
**Fix:** Use `--ls-pink-deep` for button backgrounds that need white text. It passes 4.5:1 in all themes.
**Prevention rule:** NEVER use `--ls-pink-accent` as background for white text. Use `--ls-pink-deep` instead. Pre-commit hook (`pre-commit-lint.sh`) now blocks this automatically.
**Recurrences:**
- 2026-03-08 — neurodivergent-reader popup `.site-btn:hover`, `.site-btn.active`, and settings `.btn-pink` all used `--ls-pink-accent` with white text. Prevention rule exists but wasn't followed during initial build.
- 2026-03-08 — lovespark-notes: 7 violations found. `.btn-new`, `.btn-new-dropdown`, `.font-btn.active`, `.btn-icon-sm.active`, `.version-restore`, `.format-row-btn.active`, `.cal-day.selected` — all use `--ls-pink-accent` bg with white/text-white. This is the 3rd recurrence despite existing prevention rule.
- 2026-03-08 — **shared lib** `lovespark-footer.css`: `.ls-kofi-btn` used `--ls-pink-accent` with white text. Fixed to `--ls-pink-deep`. This was in the CANONICAL shared lib, affecting all extensions. Also missing `prefers-reduced-motion` (KI-008). Both fixed + pre-commit hook now catches this.
- 2026-03-08 — **scaffold-extension.py**: Generated toggle CSS used `--ls-pink-accent` as active bg. Every newly scaffolded extension started with KI-001. Fixed to `--ls-pink-deep` in scaffold v1.1.

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
**Root cause:** Popup containers missing `role`, `aria-labelledby`, `aria-describedby`
**Fix:** Add `role="dialog"` (NOT `alertdialog`), `aria-labelledby`, and `aria-describedby` to the main popup container div. Use `alertdialog` ONLY for destructive confirmation dialogs.
**Prevention rule:** EVERY popup.html must have `role="dialog"` on its container with `aria-labelledby` pointing to the title. Do NOT use `role="alertdialog"` — it forces screen readers to announce the full describedby content on every open, which is wrong for non-modal extension panels. **Also check tools and skills** — /build-accessible and scaffold-extension.py must teach `role="dialog"`, not `alertdialog`.
**Recurrences:**
- 2026-03-08 — neurodivergent-reader and lovespark-notes both missing role on `.popup-container`.
- 2026-03-08 — /build-accessible skill was still teaching `role="alertdialog"` despite the correction below. Fixed in v1.1.
**Correction:** 2026-03-08 — Original fix prescribed `role="alertdialog"` which is semantically wrong. Code review caught this. Corrected to `role="dialog"`. Updated /build-accessible and scaffold-extension.py to match.

---

## KI-006: Focus indicators invisible or missing

**Category:** Keyboard/Focus
**Severity:** Critical
**First found:** cozy-accessibility review round 3 (2026-03)

**Symptom:** Keyboard users can't see which element is focused
**Root cause:** No `:focus-visible` styles, or browser default outline suppressed. **Systemic root cause:** `lovespark-base.css` doesn't include default `:focus-visible` styles, and `scaffold-extension.py` doesn't generate them — so extensions only get them if manually added.
**Fix:** Add `:focus-visible { outline: 2px solid var(--ls-focus-ring); outline-offset: 2px; }` on ALL interactive elements. **Systemic fix:** Add default `:focus-visible` rules to `lovespark-base.css` and update `scaffold-extension.py` to include them.
**Prevention rule:** Every CSS file must have `:focus-visible` rules for buttons, inputs, toggles, tabs, links, selects. Search for `focus-visible` in CSS before marking any UI done. **Also:** NEVER use `outline: none` without an immediately adjacent `:focus-visible` rule on the same selector. Grep for `outline: none` — every match must have a corresponding `:focus-visible` with a replacement outline.
**Recurrences:**
- 2026-03-08 — Oversight Review #1 found 15 extensions still missing `:focus-visible` (ARIA-02 check). This is the highest-hit check in the suite.
- 2026-03-08 — lovespark-notes: 7 `outline: none` suppressions in app.css and popup.css that override the global `:focus-visible` from lovespark-base.css. Affected: `#searchInput`, `.title-input`, `#tagInput`, `#noteContent`, `#commandSearch`. The base.css fix alone doesn't help when extension CSS uses `outline: none`.

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

## KI-011: innerHTML usage creates XSS risk in extensions

**Category:** Security
**Severity:** High
**First found:** Oversight Review #1 (2026-03-08)

**Symptom:** Extensions use `innerHTML` to inject content, creating potential XSS vectors
**Root cause:** Developers use `innerHTML` for convenience when building DOM dynamically. No linting or review step catches it.
**Affected extensions (8):** lovespark-notes, lovespark-motivation, lovespark-reading-mode, lovespark-focus-mode, lovespark-tab-limiter, lovespark-password-gen, lovespark-color-picker, lovespark-site-blocker (2 of these are shipped)
**Fix:** Replace `innerHTML` with `textContent` for text-only, or `createElement` + `appendChild` for structured DOM. See FIX-04 in oversight fix-patterns.md.
**Prevention rule:** NEVER use `innerHTML` in extension code. Grep for `innerHTML` before marking any extension done. Use `textContent` or DOM API methods exclusively.

---

## KI-012: Storage API mismatch between service worker and content scripts

**Category:** Functionality (Critical Bug)
**Severity:** Critical
**First found:** neurodivergent-reader Chrome Web Store rejection (2026-03-08)

**Symptom:** ALL extension features appear non-functional. Popup toggles work visually, but nothing changes on the page. Chrome Web Store reviewers rejected for "non-functional features."
**Root cause:** Service worker and popup wrote settings to `chrome.storage.local`, but content scripts (ContentOrchestrator) read from `chrome.storage.sync`. Content scripts never received any settings. The `storage.onChanged` listener also filtered for `area !== 'sync'`, missing all `local` changes.
**Fix:** Changed 4 occurrences of `sync` to `local` in ContentOrchestrator.js (get, set, onChanged filter) and service-worker.js (onChanged filter).
**Prevention rule:** All storage reads/writes in an extension MUST use the SAME storage area (`local` or `sync`). Before any extension submission, grep for `storage.sync` and `storage.local` — if BOTH appear, verify each usage is intentional. Default to `chrome.storage.local` for all LoveSpark extensions.

---

## KI-013: Dropdown triggers missing aria-expanded and aria-haspopup

**Category:** ARIA
**Severity:** High
**First found:** lovespark-notes audit (2026-03-08)

**Symptom:** Screen readers don't announce that buttons open dropdowns or whether dropdowns are open/closed
**Root cause:** Theme dropdown, template dropdown, and sync dropdown triggers lack `aria-expanded` and `aria-haspopup="true"` attributes. JS doesn't toggle `aria-expanded` on open/close.
**Fix:** Add `aria-haspopup="true"` and `aria-expanded="false"` to all dropdown trigger buttons. Toggle `aria-expanded` in JS when dropdown opens/closes.
**Prevention rule:** Every button that opens a dropdown MUST have `aria-haspopup="true"` and `aria-expanded="false"`. JS toggle code must update `aria-expanded`. Grep for `classList.toggle('open')` and verify matching `setAttribute('aria-expanded')`.

---

## KI-014: Emoji-only buttons missing aria-label

**Category:** ARIA
**Severity:** High
**First found:** lovespark-notes audit (2026-03-08)

**Symptom:** Screen readers read raw emoji instead of button purpose
**Root cause:** Buttons with only emoji text content (📋📦📥❓×) have `title` but not `aria-label`. Screen readers may not read `title`.
**Fix:** Add `aria-label` to every button whose visible text is only emoji or a symbol (×, ▾, etc.)
**Prevention rule:** Every button with emoji-only or symbol-only text MUST have `aria-label`. `title` is not sufficient. Grep for `<button.*>.[emoji]</button>` patterns and verify `aria-label` is present.

---

## KI-015: Dynamic content missing aria-live

**Category:** ARIA / Screen Reader
**Severity:** Medium
**First found:** lovespark-notes audit (2026-03-08)

**Symptom:** Screen readers don't announce save status, word count updates, or sync status changes
**Root cause:** Elements with dynamically updating text (`#saveIndicator`, `#saveStatus`, `#wordCount`, `#syncLast`) lack `aria-live` attributes
**Fix:** Add `aria-live="polite"` to all elements whose text content changes dynamically via JS
**Prevention rule:** Any element whose `textContent` is updated by JS (status messages, counters, indicators) MUST have `aria-live="polite"`. Grep for `.textContent =` and verify the target element has `aria-live`.

---

## KI-016: Form inputs relying on placeholder instead of aria-label

**Category:** ARIA / Screen Reader
**Severity:** Medium
**First found:** lovespark-notes audit (2026-03-08)

**Symptom:** Screen readers may not announce input purpose — `placeholder` is not a reliable label
**Root cause:** Inputs use `placeholder` as their only accessible name. Some screen readers don't read placeholders consistently.
**Fix:** Add `aria-label` to every `<input>` and `<textarea>` that lacks a visible `<label>`. The `aria-label` value should match the placeholder purpose.
**Prevention rule:** Every `<input>` and `<textarea>` MUST have either a visible `<label>` with matching `for`/`id`, or an `aria-label`. `placeholder` alone is insufficient.

---

## KI-017: Dual-storage theme bug — init() reads from different key than save

**Category:** Functionality (Bug)
**Severity:** Critical
**First found:** lovespark-notes (2026-03-08)

**Symptom:** Theme reverts to Retro Pink on every page load despite user selecting a different theme
**Root cause:** Theme dropdown IIFE saves to raw `chrome.storage.local` key `"theme"`, but `init()` reads from the prefs system key `"ls_prefs"` which never contains a theme property. `init()` then calls `applyTheme('retro')`, overriding the correct theme the IIFE applied.
**Fix:** Remove the redundant `applyTheme()` call from `init()` — let the IIFE be the single source of truth for theme loading. Alternatively, save theme through the prefs system.
**Prevention rule:** When a feature writes to storage, the code that reads it back MUST use the same storage key. Grep for the storage key used in save and verify the same key is used in load. Never have two competing storage mechanisms for the same setting.

---

## KI-018: aria-live on cosmetic rotating content spams screen readers

**Category:** ARIA / Screen Reader
**Severity:** High
**First found:** neurodivergent-reader code review (2026-03-08)

**Symptom:** Screen readers announce every cosmetic message rotation ("You got this!", "Stay sparkly!", etc.) every 3.5 seconds while the popup is open, creating an unusable experience.
**Root cause:** `aria-live="polite"` was added to a cosmetic rotating message element during an accessibility fix pass, without considering that `aria-live` announces ALL content changes — including decorative ones.
**Fix:** Remove `aria-live` from cosmetic/decorative rotating text elements. Only use `aria-live` on elements that convey meaningful status changes (save status, error messages, feature toggles). If both cosmetic and status messages share an element, split them.
**Prevention rule:** Before adding `aria-live` to an element, check if its content changes are **meaningful status updates** or **cosmetic decoration**. Only status updates get `aria-live`. Rotating motivational messages, cycling tips, and decorative text MUST NOT have `aria-live`.

---

## KI-019: onRuleMatchedDebug API existence check blocks polling in packed extensions

**Category:** Functionality (Critical Bug)
**Severity:** Critical
**First found:** lovespark-adblock Chrome Web Store rejection — Red Potassium (2026-03-08)

**Symptom:** "Ads blocked" counter always shows 0 in packed/CWS builds. Ad blocking works, stats don't.
**Root cause:** `if (chrome.declarativeNetRequest.onRuleMatchedDebug) return;` in `pollMatchedRules()` — the API object exists even in packed extensions (it just never fires events), so this guard always early-returns and polling never runs. Meanwhile the debug listener also never fires. Both stats paths are dead.
**Fix:** Use a runtime flag `_debugListenerFired` set inside the debug listener callback. Guard polling on `if (_debugListenerFired)` instead of API existence. Polling runs in packed extensions; debug listener takes over in unpacked.
**Prevention rule:** NEVER use API existence checks (`if (chrome.someApi)`) to decide between packed vs unpacked behavior. Chrome exposes API objects in both modes — they just don't fire events in packed builds. Use a runtime flag set inside the callback to detect if the API is actually working.

---

## KI-020: setTimeout/debounce in service workers loses data on termination

**Category:** Functionality (Data Loss)
**Severity:** High
**First found:** lovespark-adblock counter fix (2026-03-08)

**Symptom:** Stats counts intermittently lost — especially visible after brief browsing sessions
**Root cause:** `bumpStats()` accumulated counts in memory and used `setTimeout(flushStats, 500)` to debounce writes. MV3 service workers can terminate at any moment (30s inactivity, or sooner after last event). If the worker dies before `setTimeout` fires, accumulated counts are lost.
**Fix:** Write directly to storage on every stat update. Remove `setTimeout`-based debounce entirely.
**Prevention rule:** NEVER use `setTimeout` to defer storage writes in MV3 service workers. Every storage write must be durable immediately. If debouncing is needed for performance, use `chrome.alarms` (minimum 1 minute) or accept the write cost. Grep for `setTimeout` in `background.js` / service workers and verify none defer critical data writes.

---

## KI-021: Silent catch blocks hide real errors in service workers

**Category:** Code Quality / Debugging
**Severity:** Medium
**First found:** lovespark-adblock counter fix (2026-03-08)

**Symptom:** Extension appears to work but stats silently fail. No errors in console, no way to diagnose without reading source.
**Root cause:** `catch (_) {}` swallows all errors including unexpected ones (e.g., storage quota exceeded, API permission denied). Intended to handle "API not supported" but hides every possible failure.
**Fix:** Change to `catch (err) { console.warn('[ExtName] context:', err); }` — log with extension name and context.
**Prevention rule:** NEVER use empty `catch (_) {}` or `catch (e) {}` in service workers. Always log with `console.warn` including extension name and function context. Grep for `catch.*\{\s*\}` in background.js files and replace with logging.

---

## KI-022: Beige text-muted and title-override in canonical base.css fail contrast

**Category:** Contrast
**Severity:** Critical
**First found:** /improve-tools CSS parser v2.0 (2026-03-08)

**Symptom:** Beige theme muted text and header titles fail WCAG 4.5:1 in live deployed extensions. Previously masked because audit-contrast.py used hardcoded values (#6B5630, #3D5A2E) that pass, while canonical lovespark-base.css has different values (#8B6F47, #4A7C59) that fail.
**Root cause:** Canonical base.css was never updated to match the contrast-safe values from cozy-accessibility. The KI-010 sync was never completed — only documented, never fixed.
**Affected values:**
- `--ls-text-muted` in beige: base.css has #8B6F47 (3.72:1 on glass FAIL). Should be #6B5630 (5.53:1 PASS).
- `.theme-beige .header-title` color: base.css has #4A7C59 (4.24:1 on bg FAIL). Should be #3D5A2E (6.78:1 PASS).
**Fix:** Updated canonical lovespark-base.css: `--ls-text-muted` → #6B5630, `.header-title` color → #3D5A2E. Ran sync-shared-lib.sh (39 extensions synced) + audit-contrast.py (all beige checks pass now).
**Status:** FIXED (2026-03-08). CSS parser v2.0 caught this on its first run.
**Prevention rule:** Always run `audit-contrast.py` (without `--hardcoded`) after any base.css change. The CSS parser catches drift between hardcoded audit values and live CSS.

---

## Adding New Issues

When you encounter a new issue during a build or review:

1. Assign the next KI number (KI-011, etc.)
2. Fill in all fields: Category, Severity, First found, Symptom, Root cause, Fix, Prevention rule
3. The prevention rule must be actionable and specific — not "be careful"
4. If the issue should also update `debugging.md`, add it there too
5. If the issue reveals a tool gap, add it to `tool-changelog.md`
