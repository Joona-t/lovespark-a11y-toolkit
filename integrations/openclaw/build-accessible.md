# build-accessible

Use this command prompt when building LoveSpark UI.

- Include Sparky where applicable.
- Use `--ls-bg-gradient` for LoveSpark backgrounds.
- Keep touch targets at least 32x32px.
- Use a labeled "Change Theme" dropdown, not a cycling button.
- Wrap motion in `prefers-reduced-motion`.
- After implementation, run deterministic checks:
  ```bash
  python3 scripts/ls-check.py . --json
  python3 scripts/audit-contrast.py --mode tokens --json
  ```
- Fix failures and rerun until green.
