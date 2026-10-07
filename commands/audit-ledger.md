---
name: audit-ledger
description: Multi-agent post-mortem audit of the run just completed → append an honest failure entry to the Agent Audit Ledger.
---

# /audit-ledger

Run a multi-agent audit of the run/implementation that just finished, and append the result to `ledger/AGENT-AUDIT-LEDGER.md` in `lovespark-a11y-toolkit`. Use this **after every substantive run** (build, fix, debug session) — it is the self-improvement loop that turns mistakes into prevention rules + system fixes.

## Steps

1. **Build the evidence pack** from the run you just did — this is the ground truth, so be honest, not self-flattering:
   - **User corrections / frustration signals**, verbatim where possible (these are the strongest signal of where you failed — e.g. "why are you lying", "this is wrong", "you're looping", DOTS invocations).
   - **Observed agent failures**: what you *claimed* vs what was *true*; premature "done" calls; symptom-chasing; followed-bad-memory; brittle automation; unverified subagent outputs.
   - A one-line `thread` label (project + date).

2. **Run the audit workflow** (no paid API; local subagents). With the keyword `ultracode` present or multi-agent opted in:
   **EMBED the evidence inline** — author the audit as an inline `script` with the evidence pack baked into the `EVIDENCE` const (copy the structure of `workflows/thread-audit-ledger.js`). Do **NOT** rely on `{scriptPath, args}` — Workflow scripts have no filesystem access and `args.evidence` does **not** reliably bind via `scriptPath`, so the auditors silently receive the `NO EVIDENCE PASSED` sentinel and the whole run is wasted (learned the hard way; the script now has a pre-spawn guard that throws on an empty pack, but inline embedding is the fix).
   ```
   Workflow({ script: "export const meta = {...}\nconst EVIDENCE = `<the evidence pack>`\n... (5 dimension-auditors → skeptic → synthesizer)" })
   ```
   It fans out 5 dimension-auditors (verification / honesty-trust / process-DOTS / rootcause-memory / tooling-gaps) → a **skeptic** dedups and drops overclaims → a **synthesizer** returns `{ ledger_markdown, prevention_rules, system_backlog, verdict_line }`. For a clean run, tell the auditors NOT to manufacture failures to fill a quota.

3. **Prepend the entry** to `ledger/AGENT-AUDIT-LEDGER.md` (newest on top): an H2 `## <date> — <thread>`, then `ledger_markdown`, then the prevention-rules list and the system-backlog table.

4. **Privacy:** the repo is public — generalize the user's personal/health details and raw profanity; keep the **agent's** failures verbatim and unsoftened. Optionally keep a full raw copy at `~/.claude/data/agent-audit-ledger-raw.md`.

5. **Commit on a branch** (never `main`, no `Co-Authored-By`) and push; open a PR.

6. **Optionally** promote the top prevention rules into `~/.claude/docs/memory/known-issues.md` / CLAUDE.md, and file the system-backlog items for `/improve-tools`.

## Why this exists

The agent has a measured bias to under-report its own failures. A single self-review rationalizes; a 5-auditor + skeptic panel grounded in the user's real words does not. The ledger compounds: each entry teaches the next run what to avoid, and its system-backlog converts behavioral lessons into structural gates.
