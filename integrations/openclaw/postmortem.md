# postmortem

After a LoveSpark build or accessibility fix:

1. Run deterministic checks:
   ```bash
   python3 scripts/ls-check.py . --json --history
   python3 scripts/audit-contrast.py --mode tokens --json
   ```
2. Record bugs and iterations in `BUGS_AND_ITERATIONS.md`.
3. If a new class of issue escaped tooling, add a fixture and a deterministic check.
4. Keep the report concrete: problem, root cause, fix, prevention rule.
