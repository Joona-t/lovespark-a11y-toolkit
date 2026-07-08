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

## 2026-07-08 — KI-037: canonical-CSS drift detector silently dead since repo extraction

- Problem: The toolkit's two core value props were both silently broken. `audit-contrast.py`'s
  `CSS_FILE` and `ls-check.py`'s `SHARED_LIB` resolved to a hardcoded "one directory up" path
  that stopped reaching `Extensions/infrastructure/lovespark-shared-lib` the moment this toolkit
  was extracted into its own repo (`Apps & Tools/lovespark-a11y-toolkit` sits two levels below
  `Claude x LoveSpark`, not one). `audit-contrast.py` silently fell back to hardcoded token
  values every run; `ls-check`'s `BRAND-LIB-SYNC` check silently skipped every file comparison
  (`canonical.exists()` was always `False`) and reported a false "matches canonical" pass on
  every extension regardless of actual drift. This is the direct root cause of the March 2026
  `--ls-btn-bg` regression shipping stale styling to 9 extensions simultaneously with nothing
  catching it, and of the shared-lib drift finding recurring undetected across 20+ repos in 6
  independent fleet-audit batches.
- Root cause: (1) hardcoded relative-depth path assumption broke on repo extraction and nobody
  re-verified the fallback message ("CSS file not found, using hardcoded values") was actually
  firing in production; (2) a second, deeper bug found while fixing the first — even with the
  path corrected, the parser targeted `lovespark-base.css`, which no longer holds the
  `:root`/`body.theme-*` color tokens after a later shared-lib split moved them into
  `lovespark-tokens.css`; confirmed live it still parsed 0 tokens after the path fix.
- Fix: Added `find_shared_lib()` to both `scripts/audit-contrast.py` and `scripts/ls-check.py`
  (and ported to the canonical `Claude x LoveSpark/scripts/` copies per fork discipline) — walks
  up from the script's own location until it finds
  `Extensions/infrastructure/lovespark-shared-lib`, with a `LOVESPARK_SHARED_LIB` env var
  override so it survives future repo moves instead of assuming a fixed nesting depth.
  Retargeted `CSS_FILE` at `lovespark-tokens.css`. Verified live: went from "0 tokens loaded,
  silent hardcoded fallback" to "46 tokens loaded, real drift detected" (canonical hardcoded
  fallbacks in `THEMES` are themselves now shown to be slightly stale vs. live CSS — informational,
  not a regression). Strengthened `check_brand_lib_sync` (`BRAND-LIB-SYNC`) to fail loudly with an
  actionable message when the canonical directory can't be resolved at all, instead of silently
  passing. Added a new `QUAL-PAID-API` check (rule #10 grep gate: flags paid LLM API call sites
  — `api.openai.com`/`api.anthropic.com` endpoints, hardcoded `sk-`/`sk-ant-` keys, SDK client
  instantiation) to the `quality` category, which runs across every project type. Added
  `README.md`/`LICENSE`/`BUGS_AND_ITERATIONS.md` to `lovespark-shared-lib` documenting the sync
  contract, since the canonical repo the drift check depends on had none of the three. Added two
  fixture tests (`test_shared_lib_resolves_via_env_override`, `test_qual_paid_api_flags_known_violation_and_passes_clean`).
- Prevention: `find_shared_lib()`'s walk-up + env-var-override pattern is now robust against
  future repo moves by construction, not by re-verifying a hardcoded depth. The two new tests
  pin this behavior so a regression here fails CI rather than silently degrading to hardcoded
  fallbacks again. Batch-running `sync-shared-lib.sh` across the fleet with this instrument
  fixed (rather than broken) is the follow-up — flagged separately since it touches ~20 other
  repos outside this unit's assigned scope.

## 2026-07-08 — KI-039: no drift check for README test-count claims or CHANGELOG/manifest version (P2-3)

- Problem: The fleet audit found two silently stale doc claims: `lovespark-love-kana`'s README
  said `swift test # 39 unit tests` while the repo actually had 73 test functions, and
  `astrospark`'s README badge/status line claimed `20/20` unit tests against a real count of 49.
  Nothing in `ls-check` compared a README's hand-typed test-count claim against the actual test
  suite, and nothing compared a `CHANGELOG.md`'s latest version entry against `manifest.json`'s
  `version` field, so both classes of drift accrue silently exactly like the CSS-token drift
  fixed in KI-037.
- Root cause: doc claims (README test counts, CHANGELOG version headers) are hand-written at the
  moment a feature lands and nobody re-derives them later — there was no automated check wired
  into the `quality` category (the one category that runs across every project type) to catch
  either drift class.
- Fix: added `QUAL-TEST-DRIFT` (grep-counts `func test*`/`def test_*`/`it('...')`/`test('...')`
  under test-hinted paths — `Tests/`, `*Tests.swift`, `test_*.py`, etc. — across `.swift`/`.py`/
  `.js`/`.ts`, then flags any README.md line whose claimed "N tests" figure, badge, or "N/N
  tests" phrasing doesn't match) and `QUAL-CHANGELOG-DRIFT` (parses the first version-looking
  markdown heading in `CHANGELOG.md` and compares it against `manifest.json`'s `version` field)
  to `scripts/ls-check.py`'s `quality` category, wired into the existing `--strict` gate per
  fork discipline — same functions ported byte-identical into the canonical
  `Claude x LoveSpark/scripts/ls-check.py` copy. Both are `severity="warn"` (informational in a
  normal run, promoted to failures under `--strict`, matching the other `QUAL-*` doc-hygiene
  checks) so they don't break existing green CI runs that haven't opted into `--strict` yet.
  Added two fixture tests (`test_qual_test_drift_flags_stale_readme_count`,
  `test_qual_changelog_drift_flags_stale_manifest_version`). Then fixed the two live findings:
  `lovespark-love-kana` README + `audit-meta.yml` corrected from 39 to 73 (grep-verified), and
  `astrospark` README (badge + two prose mentions) corrected from 20/20 to 49/49 (grep-verified).
  Verified: `ls-check . --only quality --json` reports `QUAL-TEST-DRIFT` passing on both repos
  post-fix. Full self-audit gate green: 12 pytest passed, `py_compile` clean, `ls-check --strict`
  9/9 pass, `audit-contrast` 64/64 pass. **CORRECTED 2026-07-08, see KI-040 below: this "9/9
  pass" was measured against this repo's local `scripts/ls-check.py` copy, not the canonical
  installed `ls-check` binary the fleet actually runs — the real command failed 6/9. Do not
  trust this line as evidence of a passing self-audit; see KI-040.**
- Prevention: `QUAL-TEST-DRIFT` and `QUAL-CHANGELOG-DRIFT` now catch both drift classes on every
  future `ls-check --strict` run (the pre-CWS gate), so a stale test count or version mismatch
  fails the gate instead of shipping silently. The regex-based grep count is deliberately
  conservative (test-hinted file paths only, string-literal-first-arg for JS `it()`/`test()`) to
  avoid false positives on unrelated code (e.g. `regex.test(x)` calls).

## 2026-07-08 — KI-038: QUAL-PAID-API self-audit false positive broke CI (P1-3)

- Problem: The CI workflow's `python scripts/ls-check.py . --type python --strict` step —
  self-auditing this repo — started failing right after KI-037 landed. `QUAL-PAID-API` flagged
  `tests/test_agent_ready_toolkit.py:108`, the deliberately "dirty" fixture string
  (`"const client = new OpenAI({ apiKey: 'sk-...' })"`) that
  `test_qual_paid_api_flags_known_violation_and_passes_clean` writes into a *separate* tmp
  project directory to assert the checker catches real violations. `ls-check.py`'s own file
  scan doesn't distinguish "text that becomes a fixture file in a subprocess" from "live source
  code" — it just greps every `.py` file in the repo, including its own test file, and matched
  the fixture string as if it were a real call site in this repo's source.
- Root cause: the fixture-vs-live-code distinction has no signal `QUAL-PAID-API`'s line scanner
  can see; the existing `PAID_API_EXCLUDE_HINTS` mechanism (used elsewhere in the fleet, e.g.
  primordial's `# paid-api-gate:doc-ref` convention) covers doc/comment references but had no
  entry for "test fixture."
- Fix: tagged the fixture line with an inline `# ls-check:test-fixture (KI-037 dirty fixture,
  not live code)` comment and added `"ls-check:test-fixture"` to `PAID_API_EXCLUDE_HINTS` in
  `scripts/ls-check.py`. Verified locally: full CI step sequence (`pytest -q` → `py_compile` →
  `ls-check.py . --type python --strict` → `audit-contrast.py --mode tokens --json`) all green
  — 10 pytest passed, ls-check 7/7 pass, audit-contrast 64/64 pass, exit 0.
- Prevention: any future fixture string that deliberately trips a `QUAL-*` grep-based check
  should carry the matching `ls-check:*` exclude-hint tag on the same physical line so the
  self-audit doesn't flag its own test suite.

## 2026-07-08 — KI-040: KI-039's "ls-check --strict 9/9 pass" claim was measured against the wrong binary

- Problem: Fleet audit unit P2-lscheck-drift found that the real, installed `ls-check` command
  (`/usr/local/bin/ls-check`, which resolves to the canonical
  `Claude x LoveSpark/scripts/ls-check.py` — the copy CI and every other repo in the fleet
  actually invoke) reported **6 pass / 3 fail** under `--strict` at commit `91bbc0d`, directly
  contradicting the "ls-check --strict 9/9 pass" line logged in the KI-039 entry above. The
  claim was not fabricated so much as measured on the wrong artifact: `python3 scripts/ls-check.py
  . --strict` (this repo's own vendored copy) genuinely returns 9/9, but nobody re-ran the
  self-audit through the actual installed `ls-check` binary before writing that line down.
- Root cause: this toolkit's `scripts/ls-check.py` is a deliberate fork of the canonical copy
  (see CLAUDE.md "fork discipline" — not a byte-sync target, fixes are ported function-by-
  function). Two fixes that already existed in this repo's fork had never been ported to the
  canonical copy: (1) KI-038's `"ls-check:test-fixture"` entry in `PAID_API_EXCLUDE_HINTS`,
  causing `QUAL-PAID-API` to genuinely false-positive on this repo's own dirty test fixture
  under the canonical binary; and (2) the `/tests/` + `/scripts/` path exclusion in
  `check_python_typehints`/`check_python_docstrings` (present in this fork since the very first
  `ls-check.py` commit, `39233a7`), so the canonical copy was scoring type-hint/docstring
  coverage over this repo's `tests/` directory too — tanking `PY-TYPEHINTS` to 16/109 (15%) and
  flagging 16 "missing docstrings" that were all test helper functions never meant to be
  covered by that check.
- Fix: ported both fixes into `Claude x LoveSpark/scripts/ls-check.py` (outside git — a shared,
  non-version-controlled canonical location, not a separate repo) per fork discipline: added
  the `"ls-check:test-fixture"` hint to its `PAID_API_EXCLUDE_HINTS`, and the same `/tests/` +
  `/scripts/` path exclusion to both Python-quality functions, each with an inline comment
  noting it was ported from this fork. Bumped canonical `TOOL_VERSION` from `1.1.0` to `1.1.1`
  (its own stale-install convention) so `ls-check --version`'s hash reflects the change.
  Nothing needed changing in this repo's own `scripts/ls-check.py` — it already had both fixes;
  the drift was entirely canonical lagging behind the fork. Verified with the actual installed
  command: `ls-check . --strict` now genuinely reports **9 pass, 0 fail, 0 warn** (confirmed via
  `ls-check --version` showing the new `1.1.1` hash, not a stale cached binary). Also re-ran the
  full local gate for completeness: 12 pytest passed, `py_compile` clean, `audit-contrast --mode
  tokens --json` 64/64 pass.
- Prevention: the self-audit gate step in this repo's CI/dev workflow should invoke `ls-check`
  (the installed binary that resolves to canonical) rather than
  `python3 scripts/ls-check.py`, or explicitly document that the two can diverge and only the
  canonical run is the claim of record. Any future "N/N pass" line logged in this file for
  `ls-check --strict` should note which binary/path produced it if there's any ambiguity.

## 2026-07-09 — KI-041: A11Y-LIVE false positives — check ignored ancestor live regions
- Problem: `check_a11y_live` only checked whether the *exact opening tag* carrying a dynamic
  element's id had an `aria-live` attribute. Per WCAG/ARIA live-region semantics a live region
  announces changes to ANY descendant, so ids nested inside e.g.
  `<div class="card-section" aria-live="polite">` were wrongly flagged. Confirmed
  false-positives fleet-wide during unit R-cws-a11y-3: lovespark-affirmation-cards (4 of 5
  warnings bogus), lovespark-calm (1/1), lovespark-win-jar (6/6) — 11 of 12 warnings across the
  three repos were noise. This fork's copy was even noisier: it flagged *every* id in a file
  whenever `animateCount(` appeared anywhere.
- Root cause: regex-only tag scan has no DOM context — no way to see ancestors.
- Fix: added `_LiveRegionScanner` (stdlib `html.parser`, stack-based walk) that marks an id
  covered when its own tag OR any open ancestor declares an active live region
  (`aria-live` ≠ "off", or implicit live roles `status`/`alert`/`log`). Tolerant of malformed
  HTML (unclosed tags, stray end tags, void elements); parser output is unioned with the old
  regex pass as a floor, so coverage can only widen — genuinely uncovered ids are still
  flagged. Ported function-by-function into this fork (which also gained the canonical's
  per-variable dynamic-target detection + interactive-id suppression, replacing the
  `animateCount(` blanket match) and call site updated to pass `html_files`. Canonical
  `Claude x LoveSpark/scripts/ls-check.py` fixed identically, `TOOL_VERSION` 1.1.1 → 1.1.2.
- Verification: before/after on the three repos — 12 A11Y-LIVE warnings → 1, and the survivor
  is genuine (`#themeLabel` referenced by shared lovespark-theme.js but absent from
  affirmation-cards' popup.html). 10 synthetic edge cases pass (ancestor/deep nesting/sibling
  isolation/aria-live=off/role=status/malformed HTML/void tags/interactive/own-tag/stray end
  tag). New regression test `test_a11y_live_respects_ancestor_live_region`; suite 13/13 green.
  Installed `ls-check --version` confirms 1.1.2 (shim execs canonical directly).
- Prevention: any future HTML-structural check (ancestor/descendant relationships) must use the
  `_LiveRegionScanner` stack-walk pattern, not flat regex over tags — regex sees tags, not trees.
