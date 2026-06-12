# LoveSpark Known Issues Registry

Read this BEFORE any UI work. Every entry represents a mistake that was made, debugged, and fixed. Do not repeat them.

---

## KI-001: White text on --ls-pink-accent fails contrast in ALL themes

**Category:** Contrast
**Severity:** Critical
**First found:** cozy-accessibility build (2026-03)
**Themes affected:** ALL (retro 3.77:1, dark 2.58:1, beige 3.16:1, slate 3.35:1)
**File types:** css
**Grep pattern:** `background.*--ls-pink-accent`
**Fix pattern:** `--ls-pink-accent` → `--ls-pink-deep` in background declarations
**Auto-fixable:** yes

**Symptom:** White text on `--ls-pink-accent` buttons is hard to read
**Root cause:** `--ls-pink-accent` is designed as a decorative/highlight color, not a text-background pair. Too luminous for white text.
**Fix:** Use `--ls-pink-deep` for button backgrounds that need white text. It passes 4.5:1 in all themes.
**Prevention rule:** NEVER use `--ls-pink-accent` as background for white text. Use `--ls-pink-deep` instead. Pre-commit hook (`pre-commit-lint.sh`) now blocks this automatically.
**Recurrences:**
- 2026-03-08 — neurodivergent-reader popup `.site-btn:hover`, `.site-btn.active`, and settings `.btn-pink` all used `--ls-pink-accent` with white text. Prevention rule exists but wasn't followed during initial build.
- 2026-03-08 — lovespark-notes: 7 violations found. `.btn-new`, `.btn-new-dropdown`, `.font-btn.active`, `.btn-icon-sm.active`, `.version-restore`, `.format-row-btn.active`, `.cal-day.selected` — all use `--ls-pink-accent` bg with white/text-white. This is the 3rd recurrence despite existing prevention rule.
- 2026-03-08 — **shared lib** `lovespark-footer.css`: `.ls-kofi-btn` used `--ls-pink-accent` with white text. Fixed to `--ls-pink-deep`. This was in the CANONICAL shared lib, affecting all extensions. Also missing `prefers-reduced-motion` (KI-008). Both fixed + pre-commit hook now catches this.
- 2026-03-08 — **scaffold-extension.py**: Generated toggle CSS used `--ls-pink-accent` as active bg. Every newly scaffolded extension started with KI-001. Fixed to `--ls-pink-deep` in scaffold v1.1.
- 2026-03-10 — **focus-blossom**: 6 instances (`.btn-reblock-small`, `.btn-add`, `.btn-preset:hover`, `.back-btn`, `.btn-setting`, `.saved-toast`). Pre-existing debt — extension built before KI system. All fixed in v1.0.9 a11y pass.

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
**File types:** css
**Grep pattern:** `outline:\s*none`
**Fix pattern:** Append `:focus-visible { outline: 2px solid var(--ls-focus-ring); outline-offset: 2px; }` block
**Auto-fixable:** yes

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
**File types:** css
**Grep pattern:** `(transition|animation)\s*:`
**Fix pattern:** Append `@media (prefers-reduced-motion: reduce)` block if missing
**Auto-fixable:** yes

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
**File types:** js
**Grep pattern:** `\.innerHTML\s*=`
**Fix pattern:** Replace with `textContent` or `createElement` + `appendChild`
**Auto-fixable:** no

**Symptom:** Extensions use `innerHTML` to inject content, creating potential XSS vectors
**Root cause:** Developers use `innerHTML` for convenience when building DOM dynamically. No linting or review step catches it.
**Affected extensions (8):** lovespark-notes, lovespark-motivation, lovespark-reading-mode, lovespark-focus-mode, lovespark-tab-limiter, lovespark-password-gen, lovespark-color-picker, lovespark-site-blocker (2 of these are shipped)
**Fix:** Replace `innerHTML` with `textContent` for text-only, or `createElement` + `appendChild` for structured DOM. See FIX-04 in oversight fix-patterns.md.
**Prevention rule:** NEVER use `innerHTML` in extension code. Grep for `innerHTML` before marking any extension done. Use `textContent` or DOM API methods exclusively.
**Recurrences:**
- 2026-03-12 — lovespark-boxhead: Stored XSS via innerHTML with unsanitized player name in leaderboard. Fixed with escapeHtml() wrapper. Found by swarm audit security-scanner.

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
**File types:** js
**Grep pattern:** `catch\s*\([^)]*\)\s*\{\s*\}`
**Fix pattern:** `catch (_) {}` → `catch (err) { console.warn('[ext]', err); }`
**Auto-fixable:** yes

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

## KI-023: Wrong property name on getMatchedRules() return object

**Category:** Functionality (Critical Bug)
**Severity:** Critical
**First found:** lovespark-adblock Chrome Web Store rejection — Red Potassium (2026-03-10)

**Symptom:** Popup counter always 0 in packed extensions despite ads being blocked. Ad blocking works fine (declarativeNetRequest), but the custom counter in the popup never increments.
**Root cause:** Code reads `result.matchedRules` but the Chrome API returns `result.rulesMatchedInfo`. `result.matchedRules` is always `undefined`, so `undefined ? undefined.length : 0` evaluates to `0`. `writeStats()` is never called. Invisible during development because `onRuleMatchedDebug` in unpacked mode bypasses `pollMatchedRules()` entirely — the broken code path was dead code in dev.
**Fix:** Changed `result.matchedRules` to `result.rulesMatchedInfo` in `pollMatchedRules()`.
**Prevention rule:** ALWAYS verify Chrome API return property names against official docs before shipping. For `getMatchedRules()`, the property is `rulesMatchedInfo`, NOT `matchedRules`. More broadly: if a code path is only exercised in production (not in unpacked dev mode), add a manual test that forces the production path — e.g., set `_debugListenerFired = false` and verify polling works before submission.

---

## KI-024: getComputedStyle / document / window in 'use client' crashes SSR

**Category:** Functionality (SSR)
**Severity:** High
**First found:** Mission Control Wave 3 — AgentDesk.tsx (2026-03-11)
**Frameworks affected:** Next.js App Router

**Symptom:** Build fails or hydration error — `document is not defined` or `window is not defined` during server-side rendering
**Root cause:** `'use client'` in Next.js does NOT mean "client-only." The component still pre-renders on the server. `getComputedStyle(document.documentElement)`, `window.innerWidth`, `document.querySelector()`, etc. all crash during SSR because those browser APIs don't exist in Node.js.
**Fix:** For CSS variable values in inline styles: use the CSS var string directly (`boxShadow: '0 4px 12px var(--office-desk-shadow)'`). The browser resolves vars in inline styles at render time. For other browser APIs: wrap in `useEffect`, `typeof window !== 'undefined'` guard, or Next.js `dynamic()` with `ssr: false`.
**Prevention rule:** NEVER call `getComputedStyle`, `document.*`, or `window.*` in the render body of a React component — even if marked `'use client'`. Use CSS var strings for styling, `useEffect` for DOM access, or `typeof window !== 'undefined'` guards. Grep for `getComputedStyle\|document\.` in `.tsx` render bodies before build.

---

## KI-025: TypeScript inference breaks when removing optional property from all array items

**Category:** TypeScript / Build
**Severity:** Medium
**First found:** Mission Control Wave 3 — Sidebar.tsx (2026-03-11)

**Symptom:** `Property 'disabled' does not exist on type` error after removing `disabled: true` from all nav items
**Root cause:** When a property like `disabled` is removed from all objects in a `const` array, TypeScript infers the type without that property. Code referencing `item.disabled` (in JSX conditionals, styles, etc.) now has a type error.
**Fix:** Clean up ALL references to the removed property in the rendering code — conditionals, style expressions, aria attributes, href logic.
**Prevention rule:** When removing a property from data objects, grep the entire file for that property name and update all rendering logic in the same pass. Don't just delete the data — also delete the code that reads it.

---

## KI-026: Google Fonts CDN loaded in extension popups leaks user IP

**Category:** Privacy / Security
**Severity:** Critical
**First found:** Swarm Audit (2026-03-12)
**Extensions affected:** 35/39 at time of discovery
**File types:** html
**Grep pattern:** `href="https://(fonts\.googleapis|cdnjs\.cloudflare|gstatic)`
**Fix pattern:** Download fonts locally, replace CDN link with `lib/lovespark-fonts.css`
**Auto-fixable:** no

**Symptom:** Every popup open sends the user's IP to Google via fonts.googleapis.com. Privacy extensions (adblock, fingerprint-shield, referrer-shield) are phoning home to Google.
**Root cause:** HTML files use `<link href="https://fonts.googleapis.com/css2?...">` for DM Mono, Lora, Press Start 2P. No CSP blocks it. No one audited for external network calls.
**Fix:** Download WOFF2 files locally, create `lovespark-fonts.css` with @font-face declarations, replace CDN links with `<link rel="stylesheet" href="lib/lovespark-fonts.css">`. Fixed in swarm audit 2026-03-12.
**Prevention rule:** NEVER use external CDN links in extension HTML. ALL fonts must be bundled locally in lib/fonts/. Grep for `googleapis.com`, `gstatic.com`, `cdnjs.cloudflare.com`, or any `https://` in HTML `<link>` tags before submission. The `/audit-a11y` and `/oversight` checks should include this grep.

---

## KI-027: Zero CSP declarations across extension fleet

**Category:** Security
**Severity:** Critical
**First found:** Swarm Audit (2026-03-12)
**Extensions affected:** All 40 at time of discovery
**File types:** json
**Grep pattern:** manifest.json missing `content_security_policy`
**Fix pattern:** Insert `"content_security_policy": { "extension_pages": "script-src 'self'; object-src 'self'; font-src 'self'" }`
**Auto-fixable:** yes

**Symptom:** No Content Security Policy in any manifest.json. Extensions can load arbitrary external scripts/styles/fonts without restriction.
**Root cause:** CSP was never added to scaffold-extension.py or any existing extension. No audit check for it.
**Fix:** Added `"content_security_policy": { "extension_pages": "script-src 'self'; object-src 'self'; font-src 'self'" }` to all 39 manifests. Fixed in swarm audit 2026-03-12.
**Prevention rule:** Every manifest.json MUST have a `content_security_policy` block. scaffold-extension.py must generate it. Grep for `content_security_policy` in manifest.json before submission — if missing, it's a blocker.

---

## KI-028: Wildcard externally_connectable allows any extension to send messages

**Category:** Security
**Severity:** Critical
**First found:** Swarm Audit (2026-03-12)
**Extensions affected:** lovespark-focus, lovespark-notes (at time of discovery)

**Symptom:** Any installed browser extension can send messages to the background service worker and trigger actions (reset stats, delete tasks, write to storage) with no authentication.
**Root cause:** `"externally_connectable": { "ids": ["*"] }` in manifest.json. Plus, shared lib `setupMessageHandler()` had no sender validation.
**Fix:** Removed wildcard externally_connectable from both manifests. Added `if (sender.id !== chrome.runtime.id) return;` to shared lib setupMessageHandler(). Fixed in swarm audit 2026-03-12.
**Prevention rule:** NEVER use `"ids": ["*"]` in externally_connectable. If cross-extension messaging is needed, list specific extension IDs. All message handlers must validate sender.id. Grep for `externally_connectable` and `"ids": \["\\*"\]` before submission.

---

## KI-029: setInterval in content scripts for DOM watching

**Category:** Performance
**Severity:** High
**First found:** Swarm Audit (2026-03-12)
**Extensions affected:** 8 extensions at time of discovery (Reddit Promoted Block, popup-blocker, lovespark-focus, youtube-ad-comfort-mode, sponsor-skip, time-softener, yt-shield, shared lovespark-popup.js)

**Symptom:** Content scripts poll DOM every 1-3 seconds. Reddit Promoted Block writes to storage every 3 seconds unconditionally on every Reddit page.
**Root cause:** setInterval used for DOM monitoring instead of MutationObserver or event-based detection. Explicitly forbidden in CLAUDE.md but not enforced.
**Fix:** Replaced with MutationObserver, event listeners (yt-navigate-finish, play, loadeddata), or debounced writes triggered by actual events. Fixed 4 critical cases in swarm audit 2026-03-12.
**Prevention rule:** NEVER use setInterval in content scripts for DOM watching. Use MutationObserver or event-based detection. Grep for `setInterval` in content scripts before submission. The `/oversight` check should flag this.

---

## KI-030: Shared lib deployed everywhere but never wired up

**Category:** Architecture / Code Quality
**Severity:** High
**First found:** Swarm Audit (2026-03-12)
**Extensions affected:** 36/39 extensions

**Symptom:** 234+ dead file copies of shared lib across the ecosystem. Extensions carry all 7-8 lib files but reimplements the same logic inline (theme dropdown, CSS vars, daily reset, badge updates).
**Root cause:** sync-shared-lib.sh copies files to lib/ but nobody updates popup.html to actually load them. Extensions built before shared lib existed copied patterns inline and were never migrated.
**Fix:** Long-term: update popup.html files to link to shared CSS/JS and remove inline duplicates. Short-term: accept that some lib files are dead weight. The shared lib's theme dropdown needs a11y upgrade (from focus-blossom) before mass migration.
**Prevention rule:** When creating a new extension, scaffold-extension.py must wire popup.html to all shared lib files. For existing extensions, migration should be done per-extension during the next feature update. sync-shared-lib.sh should report adoption metrics.

---

## KI-031: Service worker sendMessage crashes when SW is asleep

**Category:** Functionality (MV3)
**Severity:** Critical
**First found:** Swarm Audit (2026-03-12)
**Extensions affected:** lovespark-focus (at time of discovery)

**Symptom:** Popup shows stale/empty state after 30 seconds of idle. Clicking buttons silently fails. No error visible to user.
**Root cause:** `chrome.runtime.sendMessage()` throws when the service worker is asleep (terminated after 30s inactivity in MV3). Popup JS has no try/catch around sendMessage calls.
**Fix:** Wrap all sendMessage calls in try/catch with retry logic. Added `safeSendMessage()` helper. Fixed in swarm audit 2026-03-12.
**Prevention rule:** EVERY `chrome.runtime.sendMessage()` call in popup.js or content scripts MUST be wrapped in try/catch. Create a `safeSendMessage()` helper and use it consistently. Grep for bare `chrome.runtime.sendMessage` without surrounding try/catch before submission.

---

## KI-011: macOS SwiftUI Menu `.borderlessButton` ignores `foregroundStyle` — use `.tint()`

**Category:** Contrast / Platform quirk
**Severity:** Critical
**First found:** Sparky beige theme fix (2026-03-29)
**Themes affected:** Beige (most visible), potentially all light themes
**File types:** swift (SwiftUI)
**Grep pattern:** `menuStyle(.borderlessButton)`
**Fix pattern:** Add `.tint(desiredColor)` to every `Menu` using `.borderlessButton`

**Symptom:** Menu label text/icons appear white or in the system accent color instead of the specified `foregroundStyle` color. On beige/light backgrounds, this makes Menu labels invisible.
**Root cause:** macOS SwiftUI's `.borderlessButton` menu style silently overrides `foregroundStyle()` on Menu labels. It uses the system tint/accent color instead. Setting `.foregroundStyle(someColor)` on the label's content has NO effect.
**Fix:** Add `.tint(desiredColor)` modifier to the `Menu` view itself — this forces macOS to use the specified color for the button label. Keep `.foregroundStyle()` as a fallback.
**Prevention rule:** EVERY `Menu` using `.menuStyle(.borderlessButton)` MUST also have a `.tint()` modifier with the desired label color. Grep for `menuStyle(.borderlessButton)` without nearby `.tint(` before shipping any SwiftUI macOS app.
**Recurrences:**
- 2026-03-29 — Sparky: 4 Menu elements affected (model selector in InputBar, theme palette in HeaderBar, sort menu in ProjectsGridView, category menu in ActivityCategoriesView). All fixed by adding `.tint()`.

---

## KI-032: Bare `catch{}` in image classifier strips pre-blur, leaks NSFW

**Category:** Browser extensions / safety / silent failures
**Severity:** P0 — user-visible safety failure
**First found:** 2026-05-09 (Rewire Brain v2.4.0 audit)
**Symptom:** Image classifier "silently fails" on Twitter/X, DuckDuckGo Images, Reddit, Imgur. User sees unblurred NSFW with no error indication.
**Root cause:** A bare `catch{}` (or `catch(e){}`) inside the image-blur pipeline removes the `rb-blur-pending` CSS class on ANY classify error. The error is swallowed; the user sees the unblurred original. Real underlying errors include:
1. `SecurityError: tainted canvas` from cross-origin images loaded without `crossOrigin="anonymous"` (the dominant case — Twitter, DDG, Reddit, Imgur all return CORS-friendly headers, but the page's `<img>` was already loaded without CORS mode)
2. CSP rejecting dynamic `<script src=>` injection on strict sites (DuckDuckGo)
3. NSFWJS bundle load failure (network or CSP)
4. TF.js WebGL backend `texImage2D` errors on low-VRAM devices

The canonical `nsfw-filter` extension has the same bug — broken on Twitter since 2020 (GitHub issue #215).

**Fix (the v2.4.2 patch):** Apply fail-closed pattern to ALL safety-layer catches:
```js
try {
  const shouldBlur = await classify(img);
  img.classList.remove('rb-blur-pending');
  if (shouldBlur) { img.classList.add('rb-blur'); /* etc */ }
} catch (err) {
  // FAIL-CLOSED: keep blur on. Never lift pre-blur on classify failure.
  console.warn('[Rewire Brain] classify failed for', img.src, '— keeping safety blur:', err);
  img.classList.remove('rb-blur-pending');
  img.classList.add('rb-blur');           // permanent blur on error
  // Optional: increment stats so user sees blur count rising even on errors
}
```

**Architectural fix (v2.5.0):** Use service-worker `fetch(url) → blob → createImageBitmap` (bypasses tainted canvas via privileged extension origin), inference in offscreen document with ONNX Runtime Web (avoids CSP issue with dynamic script injection), broaden DOM observation to catch React virtual-DOM swaps, srcset, and CSS background-images.

**Prevention rule:** Every catch block in safety-critical extension code (image classifiers, content blockers, redirects) MUST be fail-closed. Add a lint rule: any `catch` block that contains `classList.remove(SAFETY_CLASS)` without subsequently adding the same or more-restrictive class is an error. The default state on error is MORE protection, not less.

---

## KI-033: UTC date strings break streak/journal for non-UTC users

**Category:** Browser extensions / date handling / storage consistency
**Severity:** P1 — user-facing data corruption (silent)
**First found:** 2026-05-09 (Rewire Brain v2.4.0 audit)
**Symptom:** Users in non-UTC timezones see journal entries stored under the wrong calendar date; streak counts off by one. Most visible to users east of UTC during their evening hours.
**Root cause:** A common `toDateStr()` utility uses `new Date(iso).toISOString().split('T')[0]` to produce a date string. This returns UTC dates. If the same codebase uses local-clock methods elsewhere (e.g. `chrome.alarms` scheduling against `new Date().setHours(21,0,0,0)`), there's a TZ-dependent off-by-one between the two systems.
**Fix:**
```js
function toDateStr(iso) {
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

function daysBetween(dateA, dateB) {
  // Parse at LOCAL midnight (no Z) so DST transitions don't introduce ±1 hour skew
  const a = new Date(dateA + 'T00:00:00');
  const b = new Date(dateB + 'T00:00:00');
  return Math.floor((b - a) / 86400000);
}
```
**Prevention rule:** Any extension that stores date-keyed records (journal, streak, daily-cap counters) MUST use local-date strings and parse at local midnight. Never mix UTC `toISOString` with local-clock alarm scheduling. Add a lint check: if `toDateStr` uses `toISOString` AND the codebase has any `setHours(...)` calls, flag.

---

## KI-034: `chrome.runtime.sendMessage` without try/catch crashes on extension context invalidation

**Category:** Browser extensions / MV3 / error handling
**Severity:** P2 — degraded UX (silent failure of UI actions during reload)
**First found:** 2026-05-09 (Rewire Brain v2.4.0 audit, ls-check SEC-SENDMSG)
**Symptom:** When a user clicks a button immediately after the extension reloads (dev or update), the action silently fails. Console shows `Uncaught Error: Extension context invalidated` from a sendMessage call.
**Root cause:** `chrome.runtime.sendMessage` can throw synchronously if the extension context has been invalidated. Page-level scripts (popup, dashboard, options) that don't wrap calls in try/catch propagate the error and break the UI.
**Fix:** Define a `safeSend` wrapper at the top of every UI script:
```js
function safeSend(message, callback) {
  try {
    chrome.runtime.sendMessage(message, (response) => {
      if (chrome.runtime.lastError) {
        console.warn('[Extension]', message.type, 'failed:', chrome.runtime.lastError.message);
        if (callback) callback({ error: chrome.runtime.lastError.message });
        return;
      }
      if (callback) callback(response);
    });
  } catch (err) {
    console.warn('[Extension] sendMessage threw for', message.type, err);
    if (callback) callback({ error: err.message });
  }
}
```
Replace all `chrome.runtime.sendMessage(` with `safeSend(`.
**Prevention rule:** ls-check SEC-SENDMSG enforces try/catch within 5 lines. Tighten to require `try` keyword within 2 lines BEFORE the call. Better: lint should detect any `chrome.runtime.sendMessage(` not preceded by `try {` on the same statement.

---

## KI-035: Firefox AMO rejects MV3 extensions on mechanical manifest gaps

**Category:** Build/Submission (Firefox AMO)
**Severity:** Critical — every Firefox upload hits this until the manifest is patched
**First found:** AMO submission of `neurodivergent-reader-firefox.zip` (2026-05-14)
**Affected:** every LoveSpark Firefox zip prior to 2026-05-14 build pipeline patch
**File types:** manifest.json (Firefox-staged copy)
**Grep pattern:** `"service_worker"` not adjacent to `"scripts"` in same `background` block; `"data_collection_permissions"` without `"required"`
**Auto-fixable:** YES — `scripts/build-zips.sh` auto-injects fixes for Firefox-staged manifest
**Validator:** `scripts/amo-validate.py`

**Symptom:** AMO validation fails on upload with errors like:
- `"/browser_specific_settings/gecko/data_collection_permissions" must have required property 'required'`
- `Unsupported "/background/service_worker" manifest property used without "/background/scripts" property as Firefox-compatible fallback`
- (sometimes) `gecko.id missing`
- (warning) `MV3 manifest without strict_min_version`

**Root cause:** Mozilla's AMO linter has tightened MV3 requirements over 2025–2026:
- `data_collection_permissions.required` (array) became mandatory mid-2024, even when the extension collects no data — value `["none"]` is the explicit "no data" signal. `is_exempt: true` + `justification` is not enough on its own.
- Firefox's MV3 implementation doesn't fully support service workers — manifests must include `background.scripts` array pointing at the same file as `service_worker`, so Firefox runs it as a non-persistent event page.
- AMO requires `browser_specific_settings.gecko.id` (stable extension ID) — some older manifests were missing it.
- `strict_min_version` is a warning (recommended `>= 109.0` since MV3 stabilized in Firefox 109).

Chrome's CWS linter doesn't catch any of these because they're Firefox-specific. So bugs sail through Chrome submission and detonate at first AMO upload — repeatedly across the fleet.

**Fix:** Two-layer defense in `scripts/build-zips.sh`:
1. **Build-time auto-fix:** during Firefox staging, inject the 4 known fixes into the staged manifest before zipping. Lossless — only adds missing/invalid keys, never overwrites declared values that are already valid.
2. **Build-time validator gate:** after the Firefox zip is produced, run `scripts/amo-validate.py`. Exit non-zero if any `AMO-NNN` check fails. Build script propagates `exit 3`. No way to produce a broken Firefox zip through the canonical pipeline.

**Codified values** (LoveSpark fleet, local-only/privacy-first per Rule #10):
- `gecko.id = "<ext-slug>@lovespark.suite"` — auto-generated from folder basename if missing
- `gecko.data_collection_permissions.required = ["none"]` — privacy-first signal
- `background.scripts = [<service_worker>]` — duplicates SW path so Firefox treats it as an event page
- `gecko.strict_min_version = "109.0"` — first MV3-stable Firefox

**Prevention rule (HARD RULE — added to CLAUDE.md #5a 2026-05-14):**
Every `*-firefox.zip` MUST pass `scripts/amo-validate.py` before upload. The canonical build script enforces this — never bypass it, never hand-craft a Firefox zip, never upload a Firefox zip built outside this pipeline. If AMO surfaces a new rejection class, extend `amo-validate.py` with a new `AMO-NNN` check and add a KI-035-N child entry here — don't push the broken zip.

**Recurrences:**
- 2026-05-14 — `neurodivergent-reader-firefox.zip` rejected on AMO upload (AMO-001 + AMO-002). Fleet audit: 15/21 ship-now zips had AMO-001, 13/21 had AMO-002, 1/21 had AMO-004 (lovespark-tab-garden, missing gecko.id), 1/21 had AMO-001 with bad type (Anti-Brainrot, `required` not a list). Patched at the build layer; all 21 now pass.

**Tool gap closed:** before this entry, `audit-permissions.sh` and `ls-check` covered Chrome but had no AMO-specific check. Going forward, `amo-validate.py` is the authoritative Firefox preflight; `build-zips.sh` is the only sanctioned way to produce a `*-firefox.zip`.

---

## Adding New Issues

When you encounter a new issue during a build or review:

1. Assign the next KI number (KI-011, etc.)
2. Fill in all fields: Category, Severity, First found, Symptom, Root cause, Fix, Prevention rule
3. The prevention rule must be actionable and specific — not "be careful"
4. If the issue should also update `debugging.md`, add it there too
5. If the issue reveals a tool gap, add it to `tool-changelog.md`

## KI-036 — SwiftUI: stateful view re-fed a new payload at the same tree position keeps the old @State
**Category:** SwiftUI / macOS+iOS apps · **Found:** 2026-06-12, Tongue v0.5.19 guided session
**Symptom:** second kana unit's learn flow opened at card 5/5 — the previous unit's `@State index` survived because back-to-back `.kanaUnit` payloads rendered `KanaLearnView` at the same position in the view tree, so SwiftUI treated them as the same view. Items were nearly marked "introduced" without ever being displayed.
**Prevention rule:** any view holding internal `@State` that can be re-rendered with a *different payload* at the *same structural position* (sequences of intro cards, wizards, per-item editors in a switch) MUST take an explicit `.id(payload.id)` at the call site. Snapshot checks don't catch this — only live sequential interaction does; include a back-to-back-payload step in GUI walkthroughs.
