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
  9/9 pass, `audit-contrast` 64/64 pass.
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
