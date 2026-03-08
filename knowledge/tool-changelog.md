# LoveSpark Tool & Skill Changelog

Tracks what each tool/skill does, known gaps, improvement ideas, and version history.

---

## Tool: audit-contrast.py
- **Location:** `Claude x LoveSpark/scripts/audit-contrast.py`
- **Version:** 1.0 (2026-03-08)
- **What it checks:** WCAG 2.1 contrast ratios for ~20 element/background pairs across all 4 themes (retro, dark, beige, slate). Glass compositing, opacity compositing, theme title overrides.
- **What it DOESN'T check:** Actual CSS files (uses hardcoded token values). Won't catch if someone uses wrong tokens in their CSS. Won't catch new tokens added to themes. No regression detection yet.
- **Known gaps:** No history tracking between runs. Can't parse CSS directly. Doesn't check custom colors added per-extension. Doesn't verify focus-ring contrast against ALL possible backgrounds.
- **Improvement backlog:** Add --history flag for regression detection between runs. Add --update-memory flag that writes results back to color-decisions.md. Parse lovespark-base.css directly instead of hardcoded values. Add checks for any extension-specific color overrides.

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
- **Version:** 1.0 (2026-03-08)
- **What it does:** 7-step accessibility audit: contrast (runs audit-contrast.py), ARIA patterns, keyboard nav, touch targets, motion, screen reader, summary report
- **Known gaps:** Doesn't read known-issues.md first to check for recurrence. Doesn't auto-update known-issues after finding new problems. Touch target check is grep-based, not computed.
- **Improvement backlog:** Read known-issues.md at start and flag recurring issues louder. Auto-suggest KI entries for new findings. Compute actual touch target sizes from CSS values. Check against color-decisions.md dangerous pairings.

---

## Skill: /build-accessible
- **Location:** `~/.claude/commands/build-accessible.md`
- **Version:** 1.0 (2026-03-08)
- **What it does:** 6-step guide for building accessible LoveSpark UI from scratch. Loads framework, plans component tree, writes HTML/CSS/JS with canonical patterns, verifies.
- **Known gaps:** Doesn't read known-issues.md before starting. Doesn't reference color-decisions.md safe pairings. Doesn't auto-run postmortem after completion.
- **Improvement backlog:** Read known-issues.md and color-decisions.md at step 0. After verification, prompt for /postmortem. Include common mistakes checklist from known-issues.

---

## Tool: scaffold-extension.py
- **Location:** `Claude x LoveSpark/scripts/scaffold-extension.py`
- **Version:** 1.0
- **What it does:** Generates new extension skeleton with correct structure
- **Known gaps:** Generated popup.html may not include ARIA patterns. Generated CSS may not include focus-visible or reduced-motion.
- **Improvement backlog:** Include canonical accessible popup shell. Include focus-visible block and reduced-motion block in generated CSS. Include --ls-focus-ring and --ls-btn-hover-bg in generated variables.

---

## Tool: sync-shared-lib.sh
- **Location:** `Claude x LoveSpark/scripts/sync-shared-lib.sh`
- **Version:** 1.0
- **What it does:** Copies canonical shared lib to all extensions
- **Known gaps:** Doesn't run audit-contrast.py after syncing. Doesn't detect extensions with local overrides that might conflict.
- **Improvement backlog:** Run audit-contrast.py after sync as verification. Warn if destination has locally modified versions of shared files.

---

## Adding Entries

When a tool is updated:
1. Increment the version
2. Note what changed under a new "## Changes" subsection
3. Move completed items from "Improvement backlog" to the changes list
4. If a new gap is found, add it to "Known gaps"
5. If a new improvement idea comes up, add it to "Improvement backlog"
