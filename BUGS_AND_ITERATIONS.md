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
