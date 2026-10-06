# Bugs & Iterations

_No entries yet. Document bugs, fixes, and iterations here as they occur._

<!-- Format:
## YYYY-MM-DD: Short Title

**Problem:** What went wrong or needed changing
**Root cause:** Why it happened
**Fix:** What was done to resolve it
-->

## 2026-10-07 — BUG-001: public ledger leaked a machine path + un-generalized health detail (PR #4)

- **Problem:** `ledger/AGENT-AUDIT-LEDGER.md` (PR #4) carried an absolute `/Users/<name>/Projects/axion-physics/...` path in the 2026-07-02 system-backlog table, and its copy of the 2026-06-25 AI-Psychosis entry used raw wording ("24h-awake, ~90h-fasting user") that PR #1 had already generalized for this public repo — contradicting the ledger's own header ("Personal/health details are generalized").
- **Root cause:** PR #4's ledger was seeded from a copy of the entry that predates PR #1's privacy generalization (PR #1 commit `1f75f65` has the raw wording, its head `1b6f6bb` the generalized one), and the audit synthesizer wrote a local absolute path into a backlog row. Nothing scanned the ledger for `/Users/` before push.
- **Fix:** Path rewritten repo-relative (`axion-physics/scripts/validate-content.js`); the 4 drifted lines restored to PR #1's generalized wording. Regression test `tests/test_public_hygiene.py::test_ledger_has_no_machine_specific_home_paths` — fails on the pre-fix ledger (1 failed), passes after (1 passed). Reproducible check: `git grep -nE "/Users/" -- ledger/` → 0 hits.
- **Prevention:** the test runs in CI on every push. Wording drift stays a human review item (the header's promise). Pre-existing `/Users/` paths in `commands/audit-a11y.md:38` and `commands/build-accessible.md:113` are on `main` already and out of this PR's scope.
- _Placed above the chronological list on purpose: sibling PRs (#2/#3/#5) all append KI entries at the end of this file, so appending here would conflict with every one of them._

## 2026-05-23 — Agent-ready toolkit packaging

- Problem: The accessibility toolkit was useful but not installable, fixture-tested, or agent-ready.
- Root cause: CLI scripts, docs, and knowledge files had grown organically without package metadata, schema tests, or integration artifacts.
- Fix: Added Python packaging, result/file/project helper modules, pytest coverage, contrast modes, per-project history, CI, MIT LICENSE, Hermes skill artifact, and OpenClaw command artifacts.
- Prevention: Future quality-gate changes should start with fixture tests and keep legacy script paths green.
