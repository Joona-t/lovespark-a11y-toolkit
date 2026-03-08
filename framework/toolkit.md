# LoveSpark Toolkit

Check this file before every plan or implementation. Use whatever is relevant.

---

## CLI Scripts (`Claude x LoveSpark/scripts/`)

| Tool | Purpose | When to use |
|------|---------|-------------|
| `audit-contrast.py` | WCAG 2.1 contrast checker across all 4 themes. `--history` for regression detection. | Before any UI ships. After changing color tokens. |
| `audit-permissions.sh` | Checks declared vs used Chrome extension permissions. | Before Chrome Web Store submission. |
| `build-zips.sh` | Creates chrome + firefox zips for store submission. | After every extension build. |
| `bump-version.sh` | Increments patch version in manifest.json. | After any extension changes, before zipping. |
| `sync-shared-lib.sh` | Copies canonical shared lib to all extensions. | After changing anything in `lovespark-shared-lib/`. |
| `scaffold-extension.py` | Generates new extension skeleton with correct structure. | Starting a new extension. |
| `archive-plans.sh` | Archives old plan.md files. | After completing a project. |
| `council.py` | LoveSpark Senate deliberation runner. | Complex planning requiring multi-agent review. |
| `dashboard.py` | Extension suite dashboard data generator. | Checking project stats. |

## Slash Commands (`~/.claude/commands/`)

| Command | Purpose | When to use |
|---------|---------|-------------|
| `/audit-a11y` | Full 8-step accessibility audit (contrast, ARIA, keyboard, touch, motion, screen reader). Reads known-issues.md first. | Before marking any UI done. |
| `/build-accessible` | Guided accessible UI builder. Loads framework + memory, plans components, writes code, verifies. | Building any new LoveSpark popup or settings page. |
| `/postmortem` | Captures learnings after a build/review session. Updates known-issues, color-decisions, debugging, patterns, tool-changelog. | After every completed build or review. |
| `/improve-tools` | Reviews and upgrades existing tools based on accumulated knowledge. Gap analysis + targeted fixes. | After accumulating 3+ new known issues. Periodically. |

## Shared Extension Library (`Extensions/infrastructure/lovespark-shared-lib/`)

| File | Purpose | When to use |
|------|---------|-------------|
| `lovespark-base.css` | CSS variables, 4 themes, glass surfaces, theme dropdown, reduced-motion. | Every extension popup and settings page. |
| `lovespark-stats.js` | `todayStr()`, `checkDailyReset()`, debounced accumulator. | Any extension tracking counts. |
| `lovespark-badge.js` | Badge text/color with enabled/disabled/count states. | Any extension with a toolbar badge. |
| `lovespark-theme.js` | Theme dropdown handler (retro/dark/beige/slate). | Every extension with a popup UI. |
| `lovespark-popup.js` | `animateCount()`, `pop()`, `rotateMessages()`. | Every popup showing stats or messages. |
| `lovespark-lifecycle.js` | `initDefaults()`, `setupMessageHandler()`. | Every extension with background/popup communication. |

## Knowledge Base (`~/.claude/docs/memory/`)

| File | Purpose | When to read |
|------|---------|--------------|
| `known-issues.md` | Every past mistake with prevention rules. | Before any UI work. |
| `color-decisions.md` | Token values, contrast ratios, safe/dangerous pairings. | Before using any color token. |
| `tool-changelog.md` | Tool capabilities, gaps, improvement backlog. | Before `/improve-tools`. |
| `debugging.md` | Solved problems with root causes and prevention. | When hitting any bug. |
| `patterns.md` | Reusable code patterns confirmed across extensions. | When implementing common functionality. |
| `decisions.md` | Architectural decisions with rationale. | When making architecture choices. |
| `research-index.md` | Research file locations and gaps. | Before starting research on a topic. |

## Framework Docs (`~/.claude/docs/`)

| File | Purpose | When to read |
|------|---------|--------------|
| `accessibility-framework.md` | Pre-verified tokens, component patterns, hard rules, testing checklist. | Building or auditing any UI. |
| `brand.md` | Colors, typography, Sparky, UI patterns. | Building new UI. |
| `components.md` | Popup shell, stats card, toggle, button patterns. | Building extension popup/settings. |
| `architecture.md` | Manifest, permissions, file structure. | Building or auditing extensions. |
| `themes.md` | Beige, slate, dark mode specs. | Adding/modifying themes. |
| `youtube.md` | SPA nav, ad skip, SponsorBlock. | YouTube extensions. |
| `projects.md` | Current project status. | Checking what's done/in-progress. |
