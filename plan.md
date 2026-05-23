# Plan — LoveSpark A11y Toolkit Expansion

Date: 2026-05-23
Repo: `Joona-t/lovespark-a11y-toolkit`
Research source: `research.md`

## Scope

Transform `lovespark-a11y-toolkit` from an internal scripts/docs bundle into a tested, installable, agent-ready accessibility quality gate for:

- LoveSpark browser extensions
- Hermes Agent
- OpenClaw/Codex-style workflows
- CI pipelines

Preserve backwards compatibility with the current script paths:

- `scripts/ls-check.py`
- `scripts/audit-contrast.py`

## Guardrails

- Do not remove legacy entrypoints.
- Do not make default CI fail on intentionally documented forbidden contrast pair examples.
- Keep deterministic checks as the source of truth; LLMs explain/remediate after tool output.
- Treat scanned source files as untrusted data; keep evidence snippets bounded.
- Use TDD for behavior changes: write failing tests, run red, implement, run green.
- No `Co-Authored-By` lines in commits.

## Architecture

Create an importable Python package:

```text
lovespark_a11y_toolkit/
  __init__.py
  audit_contrast.py
  cli.py
  colors.py
  files.py
  history.py
  project_detection.py
  results.py
  checks/
    __init__.py
    accessibility.py
    brand.py
    ios.py
    mv3.py
    permissions.py
    python.py
    quality.py
    rust.py
    security.py
  reporters/
    __init__.py
    human.py
    json_reporter.py
```

Keep wrappers:

```text
scripts/ls-check.py
scripts/audit-contrast.py
```

Add tests:

```text
tests/
  test_project_detection.py
  test_file_collection.py
  test_results_schema.py
  test_audit_contrast.py
  test_ls_check_cli.py
  test_checks_accessibility.py
  test_checks_security.py
  test_checks_mv3.py
  test_integrations.py
  fixtures/
    extension_good/
    extension_bad_innerhtml/
    extension_bad_missing_dialog/
    extension_bad_storage_mix/
    extension_bad_motion/
    python_project/
    general_project/
```

Add integrations:

```text
integrations/hermes/SKILL.md
integrations/openclaw/audit-a11y.md
integrations/openclaw/build-accessible.md
integrations/openclaw/postmortem.md
```

Add packaging/CI:

```text
pyproject.toml
LICENSE
.github/workflows/ci.yml
```

## CLI behavior

### `ls-check`

Keep existing options:

```bash
ls-check .
ls-check . --pre-commit
ls-check . --strict
ls-check . --only accessibility
ls-check . --json
ls-check . --history
ls-check . --type extension
```

Add/normalize:

```bash
ls-check . --history-file .lovespark/ls-check-history.json
```

Default history should be per-project:

```text
<project>/.lovespark/ls-check-history.json
```

Global history only by explicit option later if needed.

### `ls-audit-contrast`

New package entrypoint:

```bash
ls-audit-contrast --mode tokens
ls-audit-contrast --mode danger-pairs
ls-audit-contrast --mode all
ls-audit-contrast --theme slate
ls-audit-contrast --json
ls-audit-contrast --css path/to/lovespark-base.css
```

Mode semantics:

- `tokens`: CI-green canonical token health checks only.
- `danger-pairs`: intentionally forbidden/dangerous combinations; useful docs/guardrails.
- `all`: everything.

Legacy wrapper `scripts/audit-contrast.py` should default to current-compatible behavior or `all`, but CI should use `--mode tokens`.

## JSON schema

All JSON reports should include:

```json
{
  "schema_version": "1.0",
  "tool": "ls-check",
  "tool_version": "0.1.0",
  "project": "name",
  "type": "extension",
  "categories": {},
  "summary": {
    "total_pass": 0,
    "total_fail": 0,
    "total_warn": 0
  }
}
```

Each result:

```json
{
  "id": "A11Y-DIALOG",
  "passed": false,
  "message": "Popup container missing role=dialog",
  "details": [],
  "severity": "fail",
  "category": "accessibility",
  "rule_source": "LoveSpark KI-005",
  "wcag": ["4.1.2"],
  "suggestion": "Add role=dialog with aria-labelledby and aria-describedby",
  "evidence": [
    {"path": "popup.html", "line": 1, "snippet": "..."}
  ]
}
```

Keep old fields compatible where possible.

## TDD implementation checklist

### Phase 1 — Packaging and compatibility

- [x] RED: test `python3 scripts/ls-check.py --help` exits 0.
- [x] RED: test `python3 scripts/audit-contrast.py --help` exits 0.
- [x] RED: test package console entrypoints can be imported.
- [x] Add `pyproject.toml` with package metadata and CLI scripts.
- [x] Add package skeleton.
- [ ] Convert legacy scripts into wrappers or keep logic while adding package imports incrementally.
- [ ] GREEN: wrapper tests pass.

### Phase 2 — Result model and JSON schema

- [x] RED: test `CheckResult.to_dict()` includes schema-ready metadata fields.
- [x] Add `results.py` dataclasses.
- [ ] Update reporters to use result objects.
- [ ] GREEN: schema tests pass.

### Phase 3 — File collection and project detection

- [x] RED: test one tree walk indexes `.html`, `.css`, `.js`, `.py` files.
- [x] RED: test ignored dirs are skipped: `.git`, `node_modules`, `.venv`, `venv`, `dist`, `build`, `.next`, `.turbo`, `coverage`, `__pycache__`.
- [x] RED: test repo with `pyproject.toml` detects as Python.
- [x] Implement indexed file collection.
- [x] Implement project detection module.
- [ ] GREEN: file/project tests pass.

### Phase 4 — Contrast modes

- [x] RED: test `--mode tokens` excludes intentional dangerous pair examples.
- [x] RED: test `--mode danger-pairs` includes white-on-pink-accent failures.
- [x] RED: test JSON includes `schema_version`, `tool`, `tool_version`, `source`, and summary.
- [ ] Move contrast logic into package module.
- [x] Add suggested fixes for known failures:
  - Slate muted text: approximate passing gray `#A1A1A1`.
  - Slate focus ring: approximate candidate `#D4834E`.
  - Beige opacity: minimum about `0.83`, keep rule recommending `0.85+`.
- [ ] GREEN: contrast tests pass.

### Phase 5 — Static checks module split

- [ ] RED: fixture tests for accessibility checks.
- [ ] RED: fixture tests for security checks.
- [ ] RED: fixture tests for MV3 checks.
- [ ] RED: fixture tests for quality checks.
- [ ] Move checks out of monolithic script by category.
- [ ] Preserve check IDs and messages where possible.
- [ ] Add `rule_source`, `wcag`, and `suggestion` metadata for high-value checks.
- [ ] GREEN: category tests pass.

### Phase 6 — History and regression tracking

- [x] RED: test default history path is project-local `.lovespark/ls-check-history.json`.
- [x] RED: test `--history-file` overrides path.
- [x] Implement per-project history.
- [ ] GREEN: history tests pass.

### Phase 7 — Hermes and OpenClaw integrations

- [x] RED: test Hermes integration `SKILL.md` has frontmatter and required commands.
- [x] RED: test OpenClaw command docs exist and mention deterministic tools.
- [x] Add `integrations/hermes/SKILL.md`.
- [x] Add `integrations/openclaw/audit-a11y.md`.
- [x] Add `integrations/openclaw/build-accessible.md`.
- [x] Add `integrations/openclaw/postmortem.md`.
- [ ] GREEN: integration tests pass.

### Phase 8 — Docs, license, CI

- [x] Add MIT `LICENSE`.
- [x] Update `README.md` with install, CLI, CI, Hermes, OpenClaw usage.
- [x] Update `BUGS_AND_ITERATIONS.md` with this iteration.
- [x] Add `.github/workflows/ci.yml`.
- [ ] CI commands:
  - `python -m py_compile scripts/*.py`
  - `python -m pytest -q`
  - `python scripts/ls-check.py . --type python --strict`
  - `python scripts/audit-contrast.py --mode tokens --json`

### Phase 9 — Verification and push

- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m py_compile scripts/*.py`.
- [ ] Run `python scripts/ls-check.py . --type python --strict`.
- [ ] Run `python scripts/audit-contrast.py --mode tokens --json`.
- [ ] Run `git diff --check`.
- [ ] Run `git status --short`.
- [ ] Commit with no co-author trailers.
- [ ] Push to `origin main`.

## Acceptance criteria

- Package installs/editable-imports locally.
- Legacy script paths still work.
- Tests cover project detection, result schema, contrast modes, representative checks, and integrations.
- Default CI path can be green.
- Contrast forbidden pair reporting remains available but no longer blocks token-health CI by default.
- Hermes Agent gets a usable skill artifact.
- OpenClaw gets command-prompt artifacts.
- README explains install and usage.
- LICENSE exists.
- Changes are committed and pushed.

## Do not implement yet

Research is complete and this plan is ready. Implementation should start only after explicit approval to proceed with implementation.
