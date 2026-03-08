# LoveSpark Accessibility Toolkit

Recursive improvement system that prevents accessibility errors during development. CLI tools, Claude Code slash commands, and a persistent knowledge base that gets smarter with every build.

## What's Inside

```
scripts/          CLI tools
  audit-contrast.py     WCAG 2.1 contrast checker (4 themes, regression detection)

framework/        Architecture docs
  accessibility-framework.md   Pre-verified tokens, component patterns, hard rules
  toolkit.md                   Master index of all LoveSpark tools and skills

commands/         Claude Code slash commands (deploy to ~/.claude/commands/)
  audit-a11y.md          Full accessibility audit (contrast + ARIA + keyboard + touch + motion)
  build-accessible.md    Guided accessible UI builder
  postmortem.md          Captures learnings after builds into knowledge base
  improve-tools.md       Reviews and upgrades tools from accumulated knowledge

knowledge/        Persistent knowledge base (deploy to ~/.claude/docs/memory/)
  known-issues.md        Every past mistake with prevention rules
  color-decisions.md     Token values, contrast ratios, safe/dangerous pairings
  tool-changelog.md      Tool capabilities, gaps, improvement backlog
```

## Usage

### Contrast Audit
```bash
python3 scripts/audit-contrast.py --verbose          # all themes
python3 scripts/audit-contrast.py --theme slate       # single theme
python3 scripts/audit-contrast.py --json              # machine-readable
python3 scripts/audit-contrast.py --history           # track regressions
```

### Claude Code Slash Commands
Copy commands to `~/.claude/commands/` to enable:
- `/audit-a11y` -- run before marking any UI done
- `/build-accessible` -- use when building new UIs
- `/postmortem` -- run after every completed build
- `/improve-tools` -- run periodically to upgrade tools

## The Feedback Loop

1. **Before building** -- read known-issues.md + color-decisions.md
2. **During building** -- use pre-verified tokens, follow framework patterns
3. **After building** -- run audit-contrast.py, then /postmortem
4. **Periodically** -- run /improve-tools to upgrade tools from accumulated knowledge

Each cycle makes the next build better. No more repeating the same mistakes.

## License

MIT
