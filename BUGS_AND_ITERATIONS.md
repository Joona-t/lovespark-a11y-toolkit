# Bugs & Iterations

_No entries yet. Document bugs, fixes, and iterations here as they occur._

<!-- Format:
## YYYY-MM-DD: Short Title

**Problem:** What went wrong or needed changing
**Root cause:** Why it happened
**Fix:** What was done to resolve it
-->

## 2026-06-28 — New check MV3-STORAGE-AREA-MATCH (KI-039)

- Problem: A live-cursor-update bug shipped in LoveSpark-Retro-Cursor — `content_script.js` registered `chrome.storage.onChanged.addListener((changes, areaName) => { if (areaName !== "sync") return; ... })` while every write went to `chrome.storage.local`. The listener was dead code, so cursor changes only applied after a page refresh. The existing MV3-STORAGE-MIX check greps for `storage.sync` substrings and passed clean — it never inspected the `onChanged` area guard.
- Root cause: No check correlated the `onChanged` `areaName` guard with the storage area the extension actually writes to. After the `storage.sync` → `storage.local` migration the guard was left pinned to the old `"sync"` value.
- Fix: Added `check_mv3_storage_area_match` (rule `MV3-STORAGE-AREA-MATCH`). It tallies `.set/.remove/.clear` per area across the whole extension and, when there is exactly one write area, FAILS any `onChanged` listener whose `areaName` guard demands a different area. Conservative — dual-area or ambiguous-guard extensions are never flagged. Wired into `run_checks` (runs in full and `--pre-commit` mode), added a `--selftest` mode, and `tests/test_storage_area_match.py`. A fleet scan with the new check immediately surfaced two more real instances (lovespark-core-notion, lovespark-youtube-ad-comfort-mode). Logged as KI-039 and propagated to post-edit-lint.sh.
- Prevention: KI-039 in known-issues.md; `python3 scripts/ls-check.py --selftest` guards against regression.

## 2026-05-23 — Agent-ready toolkit packaging

- Problem: The accessibility toolkit was useful but not installable, fixture-tested, or agent-ready.
- Root cause: CLI scripts, docs, and knowledge files had grown organically without package metadata, schema tests, or integration artifacts.
- Fix: Added Python packaging, result/file/project helper modules, pytest coverage, contrast modes, per-project history, CI, MIT LICENSE, Hermes skill artifact, and OpenClaw command artifacts.
- Prevention: Future quality-gate changes should start with fixture tests and keep legacy script paths green.
