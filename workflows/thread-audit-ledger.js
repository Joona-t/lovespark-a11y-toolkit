// thread-audit-ledger.js — multi-agent post-mortem audit of an agent run → ledger entry.
//
// Run AFTER every substantive run/implementation (via /audit-ledger, or Workflow directly).
// Pipeline: 5 parallel dimension-auditors → a skeptic (dedup + drop overclaims) → a
// synthesizer that writes the markdown ledger entry + prevention rules + system backlog.
//
// USAGE — pass the run's evidence as args.evidence (a string). Build it from the GROUND TRUTH:
//   • the user's verbatim corrections / frustration signals (these are the real signal), and
//   • the observed agent failures (what was claimed vs what was true).
//   Optionally args.thread = a one-line label.
//   Workflow({ scriptPath: ".../thread-audit-ledger.js", args: { thread: "...", evidence: "..." } })
//
// The orchestrator (caller) takes the returned { ledger } and PREPENDS it to
// ledger/AGENT-AUDIT-LEDGER.md (newest on top), then commits.
//
// Design note: the agent under-reports its own failures — the auditors are told to be
// adversarial and the skeptic is told NOT to drop a well-evidenced finding just because it's
// harsh. Local subagents only; no paid API.

export const meta = {
  name: 'thread-audit-ledger',
  description: 'Multi-agent audit of an agent thread → honest failure ledger (causes, prevention, system fixes)',
  phases: [
    { title: 'Audit', detail: '5 parallel dimension-auditors comb the evidence' },
    { title: 'Verify', detail: 'skeptic dedups, drops overclaims, ranks by severity' },
    { title: 'Synthesize', detail: 'write the ledger entry + prevention rules + system backlog' },
  ],
}

const SENTINEL = 'NO EVIDENCE PASSED'
const EVIDENCE =
  (args && args.evidence) ||
  SENTINEL + '. Pass args.evidence: a string with (1) the user\'s verbatim corrections / frustration signals and (2) the observed agent failures (claim vs reality) for the run being audited. Without it this audit cannot run.'
const THREAD = (args && args.thread) || 'untitled run'

// PRE-SPAWN EVIDENCE GUARD (ITER: caught by an audit that fanned out against the sentinel).
// Workflow scripts have NO filesystem access, and args.evidence does NOT reliably bind when this
// file is invoked via {scriptPath, args} — so evidence must be EMBEDDED inline (author the audit
// as an inline `script` with EVIDENCE filled in) or reliably passed. Fail fast here rather than
// spawning auditors against an empty pack (which wastes a full run and risks a hollow ledger entry).
if (!EVIDENCE || EVIDENCE.includes(SENTINEL) || EVIDENCE.replace(/\s/g, '').length < 200) {
  throw new Error(
    'thread-audit-ledger: evidence pack missing/empty (' + (EVIDENCE || '').length + ' chars). ' +
    'args.evidence did not bind. EMBED the evidence inline in the script (preferred — see /audit-ledger), ' +
    'or pass a non-empty args.evidence. Refusing to spawn auditors against an empty pack.'
  )
}

const DIMENSIONS = [
  { key: 'verification', brief: 'Premature completion claims — declaring a task done/fixed without verifying it on the ACTUAL failing case the user named (e.g. the worst frame).' },
  { key: 'honesty_trust', brief: 'Overclaiming that something was fixed when it was not, eroding user trust. Focus on the gap between claim and reality and its human cost.' },
  { key: 'process_dots', brief: 'Looping, latency, overthinking — violating DON\'T-OVERTHINK-SH*T; making a pressured user wait; taking many steps where one obvious move existed.' },
  { key: 'rootcause_memory', brief: 'Slow/failed root-cause diagnosis (chasing symptoms) and following/propagating INCORRECT institutional memory (a saved note prescribing a wrong fix).' },
  { key: 'tooling_gaps', brief: 'Missing automated gates/tools/checks that would have caught these; brittle automation; trusting an unverified (and wrong) subagent output.' },
]

const FINDINGS_SCHEMA = {
  type: 'object', required: ['dimension', 'findings'], additionalProperties: false,
  properties: {
    dimension: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['title', 'what', 'root_cause', 'evidence', 'severity', 'recurring', 'prevent', 'system_fix'],
        additionalProperties: false,
        properties: {
          title: { type: 'string', description: 'short imperative name of the mistake' },
          what: { type: 'string', description: 'what went wrong, concretely' },
          root_cause: { type: 'string', description: 'WHY — the underlying behavioral or system cause, not the symptom' },
          evidence: { type: 'string', description: 'the user quote or observed fact that proves it' },
          severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
          recurring: { type: 'boolean', description: 'true if likely to recur across future runs' },
          prevent: { type: 'string', description: 'a crisp BEHAVIORAL rule that would prevent it' },
          system_fix: { type: 'string', description: 'a concrete SYSTEM change (hook/script/check/gate/prompt) that makes it structurally harder' },
        },
      },
    },
  },
}

const VERDICT_SCHEMA = {
  type: 'object', required: ['confirmed', 'dropped', 'summary'], additionalProperties: false,
  properties: {
    confirmed: {
      type: 'array',
      items: {
        type: 'object', required: ['title', 'severity', 'recurring', 'why_real'], additionalProperties: false,
        properties: {
          title: { type: 'string' }, severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
          recurring: { type: 'boolean' }, why_real: { type: 'string' },
        },
      },
    },
    dropped: {
      type: 'array',
      items: { type: 'object', required: ['title', 'reason'], additionalProperties: false,
        properties: { title: { type: 'string' }, reason: { type: 'string' } } },
    },
    summary: { type: 'string', description: 'one-line quantified verdict' },
  },
}

const LEDGER_SCHEMA = {
  type: 'object', required: ['ledger_markdown', 'prevention_rules', 'system_backlog', 'verdict_line'], additionalProperties: false,
  properties: {
    verdict_line: { type: 'string' },
    ledger_markdown: { type: 'string', description: 'complete markdown body: verdict line, a table | # | Mistake | Why (root cause) | Sev | Evidence | Prevention | System fix |, then a short "Recovery pattern" paragraph' },
    prevention_rules: { type: 'array', items: { type: 'string' } },
    system_backlog: {
      type: 'array',
      items: {
        type: 'object', required: ['item', 'rationale', 'effort', 'impact'], additionalProperties: false,
        properties: {
          item: { type: 'string' }, rationale: { type: 'string' },
          effort: { type: 'string', enum: ['S', 'M', 'L'] }, impact: { type: 'string', enum: ['low', 'medium', 'high'] },
        },
      },
    },
  },
}

const auditPrompt = (d) =>
  'You are an adversarial post-mortem auditor for an AI coding/automation agent. Audit ONE dimension of a run, using ONLY the evidence pack — do not invent failures unsupported by it, and do not soften (the agent under-reports its own failures; your job is the opposite).\n\n' +
  'YOUR DIMENSION: ' + d.key + ' — ' + d.brief + '\n\n' +
  'EVIDENCE PACK:\n' + EVIDENCE + '\n\n' +
  'Return findings for YOUR dimension only: what went wrong, the ROOT CAUSE (why), the proving evidence, severity, recurring?, a crisp behavioral prevention rule, and a concrete SYSTEM fix. Be specific and unflinching.'

phase('Audit')
const audits = await parallel(
  DIMENSIONS.map((d) => () =>
    agent(auditPrompt(d), { schema: FINDINGS_SCHEMA, label: 'audit:' + d.key, phase: 'Audit' })
  )
)
const allFindings = audits.filter(Boolean).flatMap((a) => (a.findings || []).map((f) => ({ ...f, dimension: a.dimension })))
log(allFindings.length + ' raw findings across ' + audits.filter(Boolean).length + ' dimensions')

phase('Verify')
const verdict = await agent(
  'You are a skeptic verifying post-mortem findings about an AI agent run. For EACH finding decide if it is genuinely supported by the evidence or is an overclaim/duplicate. Merge near-duplicates across dimensions. DROP anything ungrounded or double-counted. Rank survivors by severity. Default to skepticism, but do NOT drop a clearly-evidenced finding just because it is harsh.\n\nEVIDENCE PACK:\n' +
    EVIDENCE + '\n\nFINDINGS TO VET (JSON):\n' + JSON.stringify(allFindings, null, 1),
  { schema: VERDICT_SCHEMA, label: 'skeptic', phase: 'Verify' }
)
log('skeptic: ' + verdict.summary)

phase('Synthesize')
const ledger = await agent(
  'You are writing the official LEDGER ENTRY for this agent run, for a self-improvement system. Be honest, concrete, outcome-first. Use the confirmed findings (overclaims/dupes already dropped) and the evidence.\n\n' +
    'THREAD: ' + THREAD + '\n\nCONFIRMED FINDINGS (JSON):\n' + JSON.stringify(verdict.confirmed, null, 1) +
    '\n\nALL RAW FINDINGS (for detail):\n' + JSON.stringify(allFindings, null, 1) +
    '\n\nEVIDENCE PACK:\n' + EVIDENCE +
    '\n\nProduce: verdict_line (one outcome-first line); ledger_markdown (verdict line, then a table | # | Mistake | Why (root cause) | Sev | Evidence | Prevention | System fix | ordered by severity, then a short "Recovery pattern" paragraph noting what finally worked so future runs copy it); prevention_rules (crisp one-liners); system_backlog (concrete tools/hooks/gates with effort S/M/L + impact). Do not fabricate beyond the evidence.',
  { schema: LEDGER_SCHEMA, label: 'synthesize', phase: 'Synthesize' }
)

return { verdict, ledger, rawFindingCount: allFindings.length }
