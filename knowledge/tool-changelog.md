# LoveSpark Tool & Skill Changelog

Tracks what each tool/skill does, known gaps, improvement ideas, and version history.

---

## Tool: audit-contrast.py
- **Location:** `Claude x LoveSpark/scripts/audit-contrast.py`
- **Version:** 2.0 (2026-03-08)
- **What it checks:** WCAG 2.1 contrast ratios for ~20 element/background pairs across all 4 themes (retro, dark, beige, slate). Glass compositing, opacity compositing, theme title overrides. **CSS parsing** from canonical lovespark-base.css (default). **Regression tracking** via `--history` flag. **Token drift detection** between hardcoded fallbacks and live CSS values.
- **What it DOESN'T check:** Extension-specific CSS overrides. Focus-ring and btn-hover-bg are still hardcoded (not defined as CSS variables in base.css).
- **Known gaps:** Doesn't check custom colors added per-extension. focus_ring and btn_hover_bg not in canonical CSS — still hardcoded. Doesn't verify focus-ring contrast against ALL possible backgrounds.
- **Improvement backlog:** Add --update-memory flag that writes results back to color-decisions.md. Upstream --ls-focus-ring and --ls-btn-hover-bg to canonical lovespark-base.css so they can be parsed. Add checks for extension-specific color overrides.
- **Changes v2.0:** Added CSS parser that reads lovespark-base.css directly. `--css PATH` flag (defaults to canonical). `--hardcoded` flag for fallback mode. Token drift warnings in `--verbose` mode. Immediately caught 4 hidden failures in beige theme (text_muted #8B6F47 and title_override #4A7C59 from canonical CSS fail contrast but hardcoded values masked them). Source tracking in history snapshots.
- **Changes v1.1:** Added `--history` flag for regression detection between runs.

---

## Tool: audit-permissions.sh
- **Location:** `Claude x LoveSpark/scripts/audit-permissions.sh`
- **Version:** 1.0 (2025)
- **What it checks:** Declared vs used permissions in manifest.json
- **Known gaps:** Only checks chrome.* API usage, not webextension-polyfill browser.* calls
- **Improvement backlog:** Support browser.* polyfill API patterns. Check content_scripts host permissions.

---

## Skill: /audit-a11y
- **Location:** `~/.claude/commands/audit-a11y.md`
- **Version:** 1.2 (2026-03-08)
- **What it does:** 8-step accessibility audit: **Step 0 loads known-issues.md + color-decisions.md**, Step 0b greps for 12 dangerous patterns (KI-001, KI-004, KI-006, KI-011, KI-012, KI-013, KI-014, KI-015, KI-016, KI-018, KI-019, KI-020, KI-021), contrast (runs audit-contrast.py --history), ARIA patterns, keyboard nav, touch targets, motion, screen reader, summary report, knowledge base update
- **Known gaps:** Touch target check is grep-based, not computed. Doesn't auto-update known-issues after finding new problems.
- **Improvement backlog:** Auto-suggest KI entries for new findings. Compute actual touch target sizes from CSS values.
- **Changes v1.2:** Added 9 new Step 0b grep checks: KI-013 (dropdown aria-expanded), KI-014 (emoji-only buttons), KI-015+KI-018 (dynamic content aria-live vs cosmetic), KI-016 (inputs without label), KI-011 (innerHTML), KI-020 (setTimeout in SW), KI-021 (empty catch), KI-019 (onRuleMatchedDebug guard), KI-006 (outline: none without focus-visible).
- **Changes v1.1:** Added Step 0b: dangerous pairing grep that catches KI-001 (pink-accent as bg), KI-004 (low opacity text), KI-012 (mixed storage APIs).

---

## Skill: /build-accessible
- **Location:** `~/.claude/commands/build-accessible.md`
- **Version:** 1.1 (2026-03-08)
- **What it does:** 6-step guide for building accessible LoveSpark UI from scratch. Loads framework + known-issues.md + color-decisions.md, plans component tree, writes HTML/CSS/JS with canonical patterns, verifies, prompts postmortem.
- **Known gaps:** Doesn't auto-run postmortem after completion.
- **Improvement backlog:** After verification, auto-invoke /postmortem.
- **Changes v1.1:** Fixed `role="alertdialog"` → `role="dialog"` (KI-005). Added KI-013, KI-014, KI-016, KI-018 patterns to Step 2.

---

## Tool: scaffold-extension.py
- **Location:** `Claude x LoveSpark/scripts/scaffold-extension.py`
- **Version:** 1.1 (2026-03-08)
- **What it does:** Generates new extension skeleton with correct structure, including accessible defaults
- **Known gaps:** Doesn't generate settings.html. Doesn't include `--ls-btn-hover-bg` in generated variables (inherited from base.css).
- **Improvement backlog:** Generate settings.html skeleton with accessible patterns. Add theme dropdown ARIA attributes to generated HTML.
- **Changes v1.1:** Fixed KI-001 (toggle bg), added role="dialog" + ARIA (KI-005), aria-label on toggle (KI-016), mascot width/height, prefers-reduced-motion block (KI-008).

---

## Tool: sync-shared-lib.sh
- **Location:** `Claude x LoveSpark/scripts/sync-shared-lib.sh`
- **Version:** 1.1 (2026-03-08)
- **What it does:** Copies canonical shared lib to all extensions. **Runs audit-contrast.py --verbose as post-sync verification.**
- **Known gaps:** Doesn't detect extensions with local overrides that might conflict.
- **Improvement backlog:** Warn if destination has locally modified versions of shared files.
- **Changes v1.1:** Added post-sync contrast audit — automatically runs `audit-contrast.py --verbose` after syncing and warns if failures found.

---

## Skill: /oversight
- **Location:** `Claude x LoveSpark/.claude/skills/oversight/SKILL.md`
- **Version:** 1.2 (2026-03-08)
- **What it does:** Self-improving daily review of all 52 LoveSpark projects. 6-phase cycle: load persistent memory → parallel project scan (3 subagents) → cross-reference against bug ledger → report → update memory → self-improve. **27 health checks** covering manifest, shared lib, git, security, storage, MV3, MV3 service worker safety, code quality, accessibility, assets, cross-project sync, roadmap.
- **Persistent memory:** `memory/oversight/` — registry.md, bug-ledger.md, fix-patterns.md, review-log.md, self-improvement.md
- **Known gaps:** Doesn't parse CSS files directly for contrast checks (relies on file presence checks). Can't detect runtime bugs (only static analysis). Doesn't integrate with CI/CD.
- **Improvement backlog:** Add CSS parsing for contrast spot-checks. Add manifest permission cross-reference against actual API usage. Track fix velocity metrics. Add per-project health trend graphs.
- **Changes v1.2:** Added MV3-SW-01 check: grep for `setTimeout` in service workers deferring storage writes (KI-020). Added MV3-SW-02 check: grep for `onRuleMatchedDebug` used as if-guard (KI-019). Added CODE-03 check: grep for empty `catch` blocks in service workers (KI-021).
- **Changes v1.1:** Added STORAGE-01 check (KI-012).

---

## Skill: /test-extension
- **Location:** `Claude x LoveSpark/.claude/skills/test-extension/SKILL.md`
- **Version:** 1.2 (2026-03-08)
- **What it does:** Manual testing checklist for Chrome extensions. Covers lifecycle (install, reload, disable/enable), **storage API consistency** (KI-012), **MV3 service worker safety** (KI-019, KI-020, KI-021), storage persistence, popup UI, content script injection, edge cases.
- **Known gaps:** Purely manual — no automation. Doesn't test Firefox-specific behavior.
- **Improvement backlog:** Add Firefox-specific test steps. Add performance benchmarks. Add automated screenshot comparison.
- **Changes v1.2:** Added 3 new storage checks: setTimeout deferring storage writes (KI-020), silent catch blocks (KI-021), API existence guards for packed/unpacked (KI-019).
- **Changes v1.1:** Added storage API consistency check (KI-012).

---

## Adding Entries

When a tool is updated:
1. Increment the version
2. Note what changed under a new "## Changes" subsection
3. Move completed items from "Improvement backlog" to the changes list
4. If a new gap is found, add it to "Known gaps"
5. If a new improvement idea comes up, add it to "Improvement backlog"
