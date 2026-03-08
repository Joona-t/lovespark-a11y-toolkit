# LoveSpark Color Token Decisions

Canonical reference for every color token value, its purpose, contrast ratios, and constraints. Read this before modifying ANY color value.

---

## Token Source Hierarchy

1. **Canonical:** `Extensions/infrastructure/lovespark-shared-lib/lovespark-base.css`
2. **Extended tokens:** `--ls-focus-ring` and `--ls-btn-hover-bg` added by cozy-accessibility, should be upstreamed to canonical
3. **Sync:** `scripts/sync-shared-lib.sh` copies canonical to all extensions
4. **Change process:** Edit canonical ONLY -> run audit-contrast.py -> fix failures -> run sync

---

## Retro Pink (Default Theme)

| Token | Value | Purpose | Contrast Notes |
|-------|-------|---------|----------------|
| --ls-bg-pink-light | #FDCFE1 | Gradient start | Lightest bg — worst case for glass compositing |
| --ls-bg-pink | #F9A8C9 | Gradient mid | text-dark on this: 6.93:1 PASS |
| --ls-bg-pink-deep | #F48CAF | Gradient end | text-dark on this: 5.57:1 PASS |
| --ls-text-dark | #5C1A36 | Body text | 9.17:1 on bg-light, 6.93:1 on bg-mid |
| --ls-text-muted | #9E4D6E | Secondary text | 4.68:1 on glass — just passes 4.5:1 |
| --ls-pink-accent | #E8457C | Decorative accent | DO NOT use as bg for white text (3.77:1 FAIL) |
| --ls-pink-deep | #D63466 | Active/pressed | Same as focus-ring and btn-hover-bg |
| --ls-focus-ring | #D63466 | Focus indicators | 3.34:1 on bg-light, 3.85:1 on glass — PASS 3:1 |
| --ls-btn-hover-bg | #D63466 | Button hover bg | White on this: 4.62:1 PASS |
| Glass composite | ~#FDE4EE | rgba(255,255,255,0.45) on #FDCFE1 | text-dark: 10.57:1 |
| Glass-strong composite | ~#FEEBF3 | rgba(255,255,255,0.6) on #FDCFE1 | text-dark: 11.11:1 |

## Dark (Noir) Theme

| Token | Value | Purpose | Contrast Notes |
|-------|-------|---------|----------------|
| --ls-bg-pink-light | #1A1128 | Gradient start (lightest) | High contrast base for light text |
| --ls-text-dark | #F0E6F6 | Body text (light on dark) | 15.03:1 on bg-light — excellent |
| --ls-text-muted | #9B7AAC | Secondary text | 5.02:1 on glass — PASS |
| --ls-pink-accent | #FF6EB4 | Decorative accent | DO NOT use as bg for white text (2.58:1 FAIL) |
| --ls-focus-ring | #FF6EB4 | Focus indicators | 7.05:1 on bg-light — excellent |
| --ls-btn-hover-bg | #C2185B | Button hover bg | White on this: 5.87:1 PASS |
| Glass composite | ~#1A0F2D | rgba(26,15,46,0.85) on #1A1128 | text-dark: 15.09:1 |

## Beige Theme

| Token | Value | Purpose | Contrast Notes |
|-------|-------|---------|----------------|
| --ls-bg-pink-light | #F5EFE0 | Solid bg (no gradient) | Warm cream |
| --ls-text-dark | #5C4A2A | Body text | 7.42:1 on bg — PASS |
| --ls-text-muted | #6B5630 (cozy) / #8B6F47 (base) | Secondary text | cozy value: 5.53:1 on glass PASS. base value: lower — needs verification |
| --ls-pink-accent | #C4806A | Decorative accent | DO NOT use as bg for white text (3.16:1 FAIL) |
| --ls-focus-ring | #7A4A35 | Focus indicators | 6.4:1 on bg — excellent |
| --ls-btn-hover-bg | #7A4A35 | Button hover bg | White on this: 7.35:1 PASS |
| Title override | #3D5A2E | Header titles | 6.78:1 on bg, 6.14:1 on glass — PASS |
| Glass (opaque) | #EDE4CE | Cards | text-dark: 6.72:1 PASS |

**KNOWN ISSUE:** Hint text at opacity 0.8 drops to 4.26:1 on glass — FAIL. See KI-004.

## Slate Theme

| Token | Value | Purpose | Contrast Notes |
|-------|-------|---------|----------------|
| --ls-bg-pink-light | #1E1E1E | Solid bg | Neutral dark gray |
| --ls-text-dark | #ECECEC | Body text (light on dark) | 14.11:1 on bg — excellent |
| --ls-text-muted | #9A9A9A | Secondary text | 5.45:1 on glass PASS, 4.17:1 on glass-strong FAIL |
| --ls-pink-accent | #D4714E | Decorative accent | DO NOT use as bg for white text (3.35:1 FAIL) |
| --ls-focus-ring | #D4714E | Focus indicators | 4.98:1 on bg, 2.65:1 on glass-border FAIL |
| --ls-btn-hover-bg | #A04520 | Button hover bg | White on this: 6.24:1 PASS |
| Title override | #E8926E | Header titles | 6.96:1 on bg, 6.4:1 on glass — PASS |
| Glass (opaque) | #252525 | Cards | text-dark: 12.98:1 PASS |
| Glass-strong (opaque) | #383838 | Selected states | text-muted: 4.17:1 FAIL (see KI-002) |

**KNOWN ISSUES:** KI-002 (muted on glass-strong), KI-003 (slider thumb on track)

---

## Universal Safe Pairings

These work in ALL 4 themes — use these by default:

| Pairing | Min Ratio (across themes) | Use For |
|---------|--------------------------|---------|
| text-dark on bg-light | 7.42:1+ | Body text on gradient |
| text-dark on glass | 6.72:1+ | Body text on cards |
| text-dark on glass-strong | 6.18:1+ | Body text on active surfaces |
| text-muted on glass | 4.68:1+ | Labels, secondary text |
| White on btn-hover-bg | 4.62:1+ | Button text |
| White on Ko-fi bg (#B92D5D) | 5.84:1 | Ko-fi donate button |
| White on danger bg (#DC3545) | 4.53:1 | Danger/delete buttons |
| focus-ring on bg-light | 3.34:1+ | Focus indicators |
| focus-ring on glass | 3.85:1+ | Focus on cards |

## Universal Dangerous Pairings

NEVER use these:

| Pairing | Worst Ratio | Why |
|---------|-------------|-----|
| White on pink-accent | 2.58:1 (dark) | Pink-accent is for decoration, not text bg |
| text-muted on glass-strong | 4.17:1 (slate) | Fails in slate |
| focus-ring on glass-border | 2.65:1 (slate) | Fails for UI components in slate |
| text-dark at 0.8 opacity on glass | 4.26:1 (beige) | Opacity reduces contrast below threshold |

---

## Changing Token Values

Before changing ANY color token:

1. Check this file for the current value and its ratios
2. Compute new ratios using `audit-contrast.py` (modify the THEMES dict temporarily)
3. Verify ALL pairings pass, not just the one you're fixing
4. Update canonical `lovespark-base.css`
5. Run `scripts/sync-shared-lib.sh`
6. Run `scripts/audit-contrast.py --verbose` to verify
7. Update this file with new ratios
8. If you broke a pairing, that's a new KI entry in known-issues.md
