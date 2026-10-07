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
- **Root cause:** PR #4's own first commit `6de6003` ("ledger: axion-content-verification audit entry") introduced both leaks: it rewrote the already-generalized 2026-06-25 AI-Psychosis lines back to raw health wording, and the audit synthesizer wrote a local absolute path into a backlog row. PR #1's commits (`1f75f65`, `1b6f6bb`) never contained either. Every later PR #4 commit up to `e8337d0` carried them; only `4be4a25` scrubs them. Nothing scanned the ledger for `/Users/` before push. _(Corrected 2026-10-07, see BUG-002: an earlier version of this line wrongly blamed PR #1 `1f75f65`.)_
- **Reproducible check:** `git log --oneline -S'90h' -- ledger/` and `git log --oneline -S'/Users/' -- ledger/` each list only `6de6003` (introduced) and `4be4a25` (removed).
- **Fix:** Path rewritten repo-relative (`axion-physics/scripts/validate-content.js`); the 4 drifted lines restored to PR #1's generalized wording. Regression test `tests/test_public_hygiene.py::test_ledger_has_no_machine_specific_home_paths` — fails on the pre-fix ledger (1 failed), passes after (1 passed). Reproducible check: `git grep -nE "/Users/" -- ledger/` → 0 hits.
- **Prevention:** the test runs in CI on every push. Wording drift stays a human review item (the header's promise). Pre-existing `/Users/` paths in `commands/audit-a11y.md:38` and `commands/build-accessible.md:113` are on `main` already and out of this PR's scope.
- _Placed above the chronological list on purpose: sibling PRs (#2/#3/#5) all append KI entries at the end of this file, so appending here would conflict with every one of them._

## 2026-10-07 — BUG-002: BUG-001 blamed the wrong commit; tip-only scrub leaves the leak in branch history (PR #4)

- **Problem:** (1) BUG-001's root cause said PR #1 commit `1f75f65` held the raw wording. False: `1f75f65` and `1b6f6bb` have 0 hits; PR #4's `6de6003` introduced it. (2) `4be4a25` only scrubs the tip. Commits `6de6003`..`e8337d0` still hold the raw health wording and the absolute path, so a merge-commit merge of PR #4 would carry them into `main`'s public history.
- **Root cause:** The root-cause sentence was written from memory, not from `git log -S`. Nobody checked per-commit history, only the tip.
- **Fix:** BUG-001's root cause now cites `6de6003` and includes the `git log -S` check. **PR #4 must be merged with `--squash`** so `main` gets only the scrubbed tree. Rewriting the branch history needs a force-push, which needs Joona's explicit OK. The PR's own commits stay visible on GitHub either way.
- **Reproducible check (after squash-merging):** `git log --oneline -S'90h' origin/main -- ledger/` and `git log --oneline -S'/Users/' origin/main -- ledger/` → 0 lines. Per commit: `for c in $(git rev-list origin/main..HEAD); do git grep -c '90h' ${c} -- ledger/; done` shows which PR commits still carry the wording.

## 2026-05-23 — Agent-ready toolkit packaging

- Problem: The accessibility toolkit was useful but not installable, fixture-tested, or agent-ready.
- Root cause: CLI scripts, docs, and knowledge files had grown organically without package metadata, schema tests, or integration artifacts.
- Fix: Added Python packaging, result/file/project helper modules, pytest coverage, contrast modes, per-project history, CI, MIT LICENSE, Hermes skill artifact, and OpenClaw command artifacts.
- Prevention: Future quality-gate changes should start with fixture tests and keep legacy script paths green.
