# Bugs & Iterations

_No entries yet. Document bugs, fixes, and iterations here as they occur._

<!-- Format:
## YYYY-MM-DD: Short Title

**Problem:** What went wrong or needed changing
**Root cause:** Why it happened
**Fix:** What was done to resolve it
-->

## 2026-05-23 — Agent-ready toolkit packaging

- Problem: The accessibility toolkit was useful but not installable, fixture-tested, or agent-ready.
- Root cause: CLI scripts, docs, and knowledge files had grown organically without package metadata, schema tests, or integration artifacts.
- Fix: Added Python packaging, result/file/project helper modules, pytest coverage, contrast modes, per-project history, CI, MIT LICENSE, Hermes skill artifact, and OpenClaw command artifacts.
- Prevention: Future quality-gate changes should start with fixture tests and keep legacy script paths green.

## 2026-06-28 — KI-LS1: stale installed `ls-check` (false PERM-MISSING on activeTab)

- **Problem:** The installed `ls-check` reported a false `PERM-MISSING: 'chrome.tabs.query' used but 'tabs' not in permissions` for extensions that correctly rely on `activeTab` (the privacy-correct pattern). Hit `Extensions/privacy/lovespark-adblock` during its v1.0.41 audit; would hit any extension using `chrome.tabs.query` + `activeTab`.
- **Root cause:** NOT the console script — it's a thin `runpy` wrapper (`lovespark_a11y_toolkit.cli:ls_check_main`), already an *editable* install, so a reinstall changes nothing. The wrapper runs this repo's `scripts/ls-check.py`. That file is a **deliberate agent-ready fork** of the canonical `Claude x LoveSpark/scripts/ls-check.py` (it keeps a versioned `--json` schema, project-local `.lovespark/` history, and a portable `--history-file`). Its check *logic*, however, had fallen behind canonical and lacked the LS-1 `tabs_satisfied` activeTab exemption in `check_perm_missing`, so it kept flagging the privacy-correct pattern.
- **Fix (surgical port — the fork's agent-ready layer is preserved):** Added the activeTab/host-permission exemption to `check_perm_missing` (`tabs_satisfied = "activeTab" in perms or bool(host_perms)`; skip the `tabs` requirement when satisfied) — the exact LS-1 logic from canonical. Added a `--version` self-check (`ls-check <ver>  sha256:<hash>`, hash of the file's own bytes) so a stale install is identifiable, and routed the JSON `tool_version` through the same `TOOL_VERSION` constant. Did **not** overwrite the file with canonical: a verbatim sync destroys the fork's versioned-schema + project-local-history design (it broke `test_*` and conflicts on history semantics — workspace wants global `~/.claude/...`, the portable toolkit wants project-local).
- **Verify:** `ls-check Extensions/privacy/lovespark-adblock` → PERM-MISSING now passes ("No missing permissions detected"); `pytest` green incl. new `test_perm_missing_accepts_activetab_without_tabs` (durable regression guard) and `test_ls_check_version_flag_emits_hash`.
- **Prevention:** The new regression test fails if the activeTab exemption ever regresses. Because this `ls-check.py` is a *fork* (not a sync target), canonical's future check-logic fixes must be **ported function-by-function**, not copied wholesale — copying clobbers the agent-ready layer.
- **Known follow-ups (not addressed here):** (1) the fork is still missing newer canonical false-positive fixes in other checks (A11Y-KI004 disabled/hover EXEMPT states; MV3-STORAGE-KEY `lastResetDate`/`checkDailyReset`; PERM-UNUSED/MV3 ES6-shorthand handling) — port on request. (2) `audit-contrast.py` diverges in the *opposite* direction (unique `--mode tokens|danger-pairs`, `suggestion_for`, `filter_checks_for_mode`) — its white-on-`pink_accent` "failures" are an intentional danger-pairs advisory, NOT a bug; leave as-is.
