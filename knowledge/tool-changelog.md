# LoveSpark Tool & Skill Changelog

Tracks what each tool/skill does, known gaps, improvement ideas, and version history.

---

## Tool: audit-contrast.py
- **Location:** `Claude x LoveSpark/scripts/audit-contrast.py`
- **Version:** 2.0 (2026-03-08)
- **What it checks:** WCAG 2.1 contrast ratios for ~20 element/background pairs across all 4 themes (retro, dark, beige, slate). Glass compositing, opacity compositing, theme title overrides. **CSS parsing** from canonical lovespark-base.css (default). **Regression tracking** via `--history` flag. **Token drift detection** between hardcoded fallbacks and live CSS values.
- **What it DOESN'T check:** Extension-specific CSS overrides.
- **Known gaps:** Doesn't check custom colors added per-extension. Doesn't verify focus-ring contrast against ALL possible backgrounds. CSS parser doesn't yet read --ls-focus-ring and --ls-btn-hover-bg (now in canonical CSS as of 2026-03-17 — parser VAR_MAP needs update).
- **Improvement backlog:** Add --update-memory flag that writes results back to color-decisions.md. Add --ls-focus-ring and --ls-btn-hover-bg to VAR_MAP in CSS parser. Add checks for extension-specific color overrides.
- **Changes v2.0:** Added CSS parser that reads lovespark-base.css directly. `--css PATH` flag (defaults to canonical). `--hardcoded` flag for fallback mode. Token drift warnings in `--verbose` mode. Immediately caught 4 hidden failures in beige theme (text_muted #8B6F47 and title_override #4A7C59 from canonical CSS fail contrast but hardcoded values masked them). Source tracking in history snapshots.
- **Changes v1.1:** Added `--history` flag for regression detection between runs.

---

## Tool: ls-check.py
- **Location:** `Claude x LoveSpark/scripts/ls-check.py`
- **Version:** 1.0 (2026-03-17)
- **What it does:** Unified quality pipeline. Auto-detects project type (extension, Rust, Python, iOS, web, general) and runs relevant checks. 38 checks across 8 categories: accessibility (12), security (6), MV3 (6), brand (5), permissions (2), quality (4), Rust (3), Python (2). Replaces manual audit loops with single command. Delegates contrast audit to audit-contrast.py. Supports `--pre-commit` (fast, <2s), `--strict` (warnings=failures for CWS submission), `--only CATEGORY`, `--json`, `--history` (regression detection).
- **Known gaps:** Touch target check is presence-based (trusts base.css), not computed pixel sizes. A11Y-LIVE is heuristic — flags dynamic textContent targets but can't verify HTML aria-live attributes from JS alone. Permission checks don't cover webextension-polyfill browser.* API patterns.
- **Improvement backlog:** Add `--fix` flag for auto-fixable issues (e.g., adding CSP to manifest). Add CANDIDATE KI output for novel patterns. Add GitHub Actions workflow template. Dashboard integration.

---

## Hook: post-edit-lint.sh
- **Location:** `~/.claude/hooks/post-edit-lint.sh`
- **Version:** 3.0 (2026-03-20)
- **What it does:** PostToolUse hook on Write/Edit/MultiEdit. Fast KI violation grep on just-edited files. **v3.0: Now BLOCKS on critical violations** (KI-001, KI-027) via JSON `{"decision":"block"}` protocol. Warns on non-critical KIs via `{"additionalContext":"..."}`. Supports CSS, HTML, JS, and Swift files.
- **Checks:** KI-001 (CRITICAL), KI-005, KI-006, KI-008, KI-011, KI-020, KI-021, KI-026, KI-027 (CRITICAL), KI-029, KI-031, IKI-001, IKI-016, try!, force unwraps.
- **Changes v3.0:** Upgraded from warn-only to blocking. Added JSON output protocol. Added Swift file support (IKI-001, IKI-016, try!, force unwraps). Added KI-031 (bare sendMessage).

---

## Hook: post-edit-swift.sh
- **Location:** `~/.claude/hooks/post-edit-swift.sh`
- **Version:** 1.0 (2026-03-20)
- **What it does:** PostToolUse hook for Swift files. Checks that new .swift files are registered in project.pbxproj by running `sync-xcode-sources.py --check`. **BLOCKS if unregistered files found** (IKI-012).

---

## Hook: pre-impl-gate.sh
- **Location:** `~/.claude/hooks/pre-impl-gate.sh`
- **Version:** 1.0 (2026-03-20)
- **What it does:** PreToolUse hook on Write/Edit. Injects relevant Known Issue reminders before code is written. CSS → KI-001/006/008. HTML → KI-005/026/027. JS → KI-011/020/021/029/031. Swift → IKI-001/015/016/017. Never blocks.

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
- **Version:** 1.3 (2026-03-11)
- **What it does:** 8-step accessibility audit: **Step 0 loads known-issues.md + color-decisions.md**, Step 0b greps for 14 dangerous patterns (KI-001, KI-004, KI-006, KI-011, KI-012, KI-013, KI-014, KI-015, KI-016, KI-017, KI-018, KI-019, KI-020, KI-021, KI-023), contrast (runs audit-contrast.py --history), ARIA patterns, keyboard nav, touch targets, motion, screen reader, summary report, knowledge base update
- **Known gaps:** Touch target check is grep-based, not computed. Doesn't auto-update known-issues after finding new problems.
- **Improvement backlog:** Auto-suggest KI entries for new findings. Compute actual touch target sizes from CSS values.
- **Changes v1.3:** Added 2 new Step 0b checks: KI-023 (`.matchedRules` → `.rulesMatchedInfo` grep), KI-017 (storage key mismatch between save/load paths).
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
- **Version:** 2.0 (2026-03-17)
- **What it does:** Generates new extension skeleton with correct structure, including accessible defaults. v2.0: CSP in manifest, no CDN fonts (system stack), full ARIA on theme dropdown (aria-expanded, aria-haspopup, role=menu/menuitem), aria-live on stat counters, aria-label on stat boxes, optional `--settings` flag.
- **Known gaps:** Make directory existence check more tolerant — allow pre-existing empty or partially-populated directories (swarm-build.py needs this).
- **Improvement backlog:** Make directory existence check more tolerant.
- **Changes v2.0:** Added CSP to manifest (KI-027). Removed CDN Google Fonts links (KI-026). Added aria-expanded + aria-haspopup to theme dropdown. Added aria-live="polite" on stat counters. Added aria-label on stat boxes. Added --settings flag for settings.html skeleton. Theme dropdown now uses dropdown menu pattern (role=menu/menuitem) instead of cycling button.
- **Changes v1.1:** Fixed KI-001 (toggle bg), added role="dialog" + ARIA (KI-005), aria-label on toggle (KI-016), mascot width/height, prefers-reduced-motion block (KI-008).

---

## Tool: sync-shared-lib.sh
- **Location:** `Claude x LoveSpark/scripts/sync-shared-lib.sh`
- **Version:** 2.0 (2026-03-17)
- **What it does:** Copies canonical shared lib to all extensions. Checksum verification after copy. Local modification detection. `--dry-run` and `--force` flags. Post-sync contrast audit.
- **Known gaps:** Adoption metrics output to stderr (intended for piping, not display).
- **Improvement backlog:** Add adoption report summary at end of output.
- **Changes v2.0:** Added MD5 checksum verification after every copy. Added local modification detection (warns before overwriting). Added `--dry-run` flag. Added `--force` flag. Added colored output.
- **Changes v1.1:** Added post-sync contrast audit — automatically runs `audit-contrast.py --verbose` after syncing and warns if failures found.

---

## Skill: /oversight
- **Location:** `Claude x LoveSpark/.claude/skills/oversight/SKILL.md`
- **Version:** 1.3 (2026-03-11)
- **What it does:** Self-improving daily review of all 52 LoveSpark projects. 6-phase cycle: load persistent memory → parallel project scan (3 subagents) → cross-reference against bug ledger → report → update memory → self-improve. **29 health checks** covering manifest, shared lib, git, security, storage, DNR API safety, MV3, MV3 service worker safety, code quality, accessibility, assets, cross-project sync, roadmap.
- **Persistent memory:** `memory/oversight/` — registry.md, bug-ledger.md, fix-patterns.md, review-log.md, self-improvement.md
- **Known gaps:** Doesn't parse CSS files directly for contrast checks (relies on file presence checks). Can't detect runtime bugs (only static analysis). Doesn't integrate with CI/CD. Doesn't check for external CDN links in HTML (KI-026). Doesn't check for CSP in manifests (KI-027). Doesn't check for wildcard externally_connectable (KI-028). Doesn't check for bare sendMessage without try/catch (KI-031).
- **Improvement backlog:** Add CSS parsing for contrast spot-checks. Add manifest permission cross-reference against actual API usage. Track fix velocity metrics. Add per-project health trend graphs. Add CDN-01 check: grep for `googleapis.com|gstatic.com|cdnjs.cloudflare.com` in HTML (KI-026). Add SEC-01 check: grep manifests for `content_security_policy` (KI-027). Add SEC-02 check: grep manifests for `externally_connectable.*\*` (KI-028). Add MV3-SW-03 check: grep for bare `sendMessage` without try/catch (KI-031). Add PERF-01 check: grep for `setInterval` in content scripts (KI-029).
- **Changes v1.3:** Added DNR-01 check: grep for `.matchedRules` which should be `.rulesMatchedInfo` (KI-023). Added STORAGE-02 check: detect storage key mismatch between save and load paths for the same setting (KI-017). Total checks: 29.
- **Changes v1.2:** Added MV3-SW-01 check: grep for `setTimeout` in service workers deferring storage writes (KI-020). Added MV3-SW-02 check: grep for `onRuleMatchedDebug` used as if-guard (KI-019). Added CODE-03 check: grep for empty `catch` blocks in service workers (KI-021).
- **Changes v1.1:** Added STORAGE-01 check (KI-012).

---

## Skill: /test-extension
- **Location:** `Claude x LoveSpark/.claude/skills/test-extension/SKILL.md`
- **Version:** 1.3 (2026-03-11)
- **What it does:** Manual testing checklist for Chrome extensions. Covers lifecycle (install, reload, disable/enable), **storage API consistency** (KI-012), **MV3 service worker safety** (KI-019, KI-020, KI-021), **Chrome API property verification** (KI-023), **storage key mismatch detection** (KI-017), **production code path testing**, storage persistence, popup UI, content script injection, edge cases.
- **Known gaps:** Purely manual — no automation. Doesn't test Firefox-specific behavior.
- **Improvement backlog:** Add Firefox-specific test steps. Add performance benchmarks. Add automated screenshot comparison.
- **Changes v1.3:** Added Chrome API return property name verification check (KI-023). Added storage key mismatch test between save/load paths (KI-017). Added production-only code path testing check (KI-023).
- **Changes v1.2:** Added 3 new storage checks: setTimeout deferring storage writes (KI-020), silent catch blocks (KI-021), API existence guards for packed/unpacked (KI-019).
- **Changes v1.1:** Added storage API consistency check (KI-012).

---

## Tool: lsmemory
- **Location:** `Claude x LoveSpark/Apps & Tools/lsmemory/lsmemory.py`
- **Symlink:** `~/.local/bin/lsmemory`
- **Version:** 1.0 (2026-03-10)
- **What it does:** Git-backed learning-across-sessions memory system. Stores observations, patterns, gotchas, decisions as JSONL entries with reversible source refs. Two layers: global (~/.lsmemory/global.jsonl) + per-project (~/.lsmemory/projects/*.jsonl). Commands: init, store, recall, list, compress, sync, extract, import-senate, import-markdown, config.
- **Known gaps:** Auto-extraction (`extract`) not yet tested end-to-end (requires `claude -p` call). Markdown import parser is basic (splits on headings/---). No search by date range. No `delete` command for removing bad entries.
- **Improvement backlog:** Add PostStopSession hook for auto-extraction (v1.1). Add `lsmemory delete ID` command. Add `lsmemory search` for full-text search. Add `--since DATE` filter to list. Test extract pipeline with real session transcript.

---

## Skill: /learn
- **Location:** `~/.claude/commands/learn.md`
- **Version:** 1.0 (2026-03-10)
- **What it does:** Manual memory storage from Claude Code sessions. Wraps `lsmemory store` with auto-detection of project from cwd. Supports --type, --tags, --scope flags.
- **Known gaps:** Can't auto-tag based on observation content. No confirmation of dedup when merging.
- **Improvement backlog:** Auto-suggest tags from observation keywords. Show dedup info when a merge happens.

---

## Skill: /recall
- **Location:** `~/.claude/commands/recall.md`
- **Version:** 1.0 (2026-03-10)
- **What it does:** Memory retrieval for Claude Code sessions. Wraps `lsmemory recall` with dual-scope search. Supports --max-chars, --scope, --json flags.
- **Known gaps:** Doesn't auto-invoke at session start. No way to boost/demote specific memories from the skill.
- **Improvement backlog:** Consider auto-recall at session start for projects with >5 memories. Add feedback mechanism (was this memory helpful? → boost confidence).

---

## Skill: /swarm-audit
- **Location:** `~/.claude/commands/swarm-audit.md` + project-level
- **Version:** 1.0 (2026-03-12)
- **What it does:** Full ecosystem audit deploying 12 specialists (Sonnet) + 6 council leads (Opus) in 4-wave pattern. Scans all extensions for performance, reliability, code quality, brand, security, dependencies, patterns, docs, assets, manifests, privacy, dead code.
- **Known gaps:** No automated re-verification after fixes (manual grep needed). Doesn't integrate with CI/CD. Reports are markdown files, not structured data.
- **Improvement backlog:** Add automated post-fix verification wave. Add structured JSON output for dashboard integration. Add delta mode (only scan changed files since last audit).

---

## Skill: /ship-day
- **Location:** `~/.claude/commands/ship-day.md` + project-level
- **Version:** 1.0 (2026-03-12)
- **What it does:** Release pipeline for one extension. Full council + specialists with focus on store readiness, then generates zips and ship report.
- **Known gaps:** Not yet tested end-to-end.
- **Improvement backlog:** Add automated store screenshot generation. Add Chrome/Firefox/Edge submission checklist.

---

## Skill: /council-review
- **Location:** `~/.claude/commands/council-review.md` + project-level
- **Version:** 1.0 (2026-03-12)
- **What it does:** Deep review of one extension by all 6 council leads + relevant specialists.
- **Known gaps:** Not yet tested end-to-end.
- **Improvement backlog:** None yet.

---

## Skill: /brand-sweep
- **Location:** `~/.claude/commands/brand-sweep.md` + project-level
- **Version:** 1.0 (2026-03-12)
- **What it does:** Brand consistency sweep across entire ecosystem. Rauch + brand-auditor + asset-validator + docs-generator + cross-sync.
- **Known gaps:** Not yet tested end-to-end.
- **Improvement backlog:** None yet.

---

## Skill: /quick-fix
- **Location:** `~/.claude/commands/quick-fix.md` + project-level
- **Version:** 1.0 (2026-03-12)
- **What it does:** Targeted fix on one extension. Skips full recon, deploys 1-3 relevant specialists + council lead.
- **Known gaps:** Not yet tested end-to-end.
- **Improvement backlog:** None yet.

---

## Skill: /swarm-build
- **Location:** `~/.claude/commands/swarm-build.md`
- **Version:** 1.0 (2026-03-12)
- **What it does:** Build orchestration for the 22-agent swarm. Two modes: `new` (scaffold + full design pipeline) and `feature` (add to existing extension). 4-wave adapted pattern: Wave 1 (Research, 12 parallel specialists), Wave 2 (Iterative Design, 3-round council cross-feed), Wave 3 (Linus Gate GO/NO-GO), Wave 4 (Build with non-overlapping file scopes). Hard stop between design and implementation.
- **Known gaps:** Not yet tested end-to-end with a real build. Cross-feed round 2 relies on Claude Code context window being large enough to hold all 6 leads' output.
- **Improvement backlog:** Add estimated token cost tracking per wave. Add wave-specific report templates.

---

## Tool: swarm-build.py
- **Location:** `Claude x LoveSpark/scripts/swarm-build.py`
- **Version:** 1.0 (2026-03-12)
- **What it does:** Standalone CLI companion for /swarm-build. Scaffolds directories, generates research.md/plan.md/BUILD-RECON templates, tracks wave state in `.swarm-build-state.json`, runs post-build audits. 5 subcommands: new, feature, status, resume, audit.
- **Known gaps:** `new` mode runs scaffold-extension.py but must handle the directory-exists ordering issue (scaffold must run first). `resume` only searches extension directories, not arbitrary paths. No wave state transitions from CLI (tracked but not updated — Claude Code sessions update state).
- **Improvement backlog:** Add `swarm-build.py wave-complete [wave]` command to update state from CLI. Add `--dry-run` flag. Add scaffold-extension.py tolerance for pre-existing directories (upstream fix).

---

## Skill: /forge-skill
- **Location:** `~/.claude/commands/forge-skill.md`
- **Version:** 1.0 (2026-03-15)
- **What it does:** Meta-skill that creates new CLI skills on the fly. Parses name, scope (global/project), purpose, and optional --template flag. Validates kebab-case, checks for duplicates, selects from 6 embedded template skeletons (audit, build, research, fix, swarm-dispatch, utility), generates the .md file, and registers it in tool-changelog.md. Integrates with swarm via FORGE CANDIDATE logging protocol.
- **Known gaps:** Newly created — not yet tested end-to-end. Cannot create directory-based skills (SKILL.md + reference files). Cannot modify existing skills (use /improve-tools for that).
- **Improvement backlog:** Add --dry-run flag to preview without writing. Add skill usage tracking. Add template preview command.

---

## Skill: /test-forge-research
- **Location:** `~/.claude/commands/test-forge-research.md`
- **Version:** 1.0 (2026-03-15)
- **What it does:** Investigate a topic and write findings to research.md
- **Generated by:** /forge-skill (template: research)
- **Known gaps:** Newly generated — not yet tested end-to-end.
- **Improvement backlog:** Test and refine based on first real usage.

---

## Adding Entries

When a tool is updated:
1. Increment the version
2. Note what changed under a new "## Changes" subsection
3. Move completed items from "Improvement backlog" to the changes list
4. If a new gap is found, add it to "Known gaps"
5. If a new improvement idea comes up, add it to "Improvement backlog"
