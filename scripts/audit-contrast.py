#!/usr/bin/env python3
"""LoveSpark Contrast Audit — WCAG 2.1 contrast checker for all 4 themes.

Zero external dependencies. Uses relative luminance formula per WCAG 2.1.
Reads token values from canonical lovespark-base.css when available,
falls back to hardcoded values otherwise.

Features:
  --history: Save results and detect regressions between runs
  --hardcoded: Skip CSS parsing, use hardcoded fallback values
  Persistent history at ~/.claude/docs/memory/contrast-history.json

Usage:
    python3 audit-contrast.py [--theme THEME] [--verbose] [--json] [--history]
    python3 audit-contrast.py --css /path/to/lovespark-base.css --verbose
"""

import argparse
import json
import os
import re
import sys
from datetime import date

# ── Canonical CSS Path ─────────────────────────────────────────────────────

CSS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "Extensions", "infrastructure", "lovespark-shared-lib",
    "lovespark-base.css"
)

# ── Theme Palettes (hardcoded fallbacks) ───────────────────────────────────
# These serve as documentation AND fallback when CSS file isn't available.
# CSS parser overrides these with live values from lovespark-base.css.

THEMES = {
    "retro": {
        "bg_light":      (0xFD, 0xCF, 0xE1),
        "bg_mid":        (0xF9, 0xA8, 0xC9),
        "bg_deep":       (0xF4, 0x8C, 0xAF),
        "text_dark":     (0x5C, 0x1A, 0x36),
        "text_muted":    (0x9E, 0x4D, 0x6E),
        "pink_accent":   (0xE8, 0x45, 0x7C),
        "focus_ring":    (0xD6, 0x34, 0x66),
        "btn_hover_bg":  (0xD6, 0x34, 0x66),
        "glass_composite":        None,  # computed below
        "glass_strong_composite": None,
        "glass_border_composite": None,
        "glass_light_composite":  None,
        "_glass_rgb":   (255, 255, 255), "_glass_a": 0.45,
        "_glass_s_rgb": (255, 255, 255), "_glass_s_a": 0.6,
        "_glass_b_rgb": (255, 255, 255), "_glass_b_a": 0.4,
        "_glass_l_rgb": (255, 255, 255), "_glass_l_a": 0.25,
        "_worst_bg":    (0xFD, 0xCF, 0xE1),
    },
    "dark": {
        "bg_light":      (0x1A, 0x11, 0x28),
        "bg_mid":        (0x11, 0x0D, 0x1A),
        "bg_deep":       (0x0A, 0x08, 0x12),
        "text_dark":     (0xF0, 0xE6, 0xF6),
        "text_muted":    (0x9B, 0x7A, 0xAC),
        "pink_accent":   (0xFF, 0x6E, 0xB4),
        "focus_ring":    (0xFF, 0x6E, 0xB4),
        "btn_hover_bg":  (0xC2, 0x18, 0x5B),
        "glass_composite":        None,
        "glass_strong_composite": None,
        "glass_border_composite": None,
        "glass_light_composite":  None,
        "_glass_rgb":   (26, 15, 46), "_glass_a": 0.85,
        "_glass_s_rgb": (26, 15, 46), "_glass_s_a": 0.95,
        "_glass_b_rgb": (255, 110, 180), "_glass_b_a": 0.13,
        "_glass_l_rgb": (26, 15, 46), "_glass_l_a": 0.5,
        "_worst_bg":    (0x1A, 0x11, 0x28),
    },
    "beige": {
        "bg_light":      (0xF5, 0xEF, 0xE0),
        "bg_mid":        (0xF5, 0xEF, 0xE0),
        "bg_deep":       (0xED, 0xE4, 0xCE),
        "text_dark":     (0x5C, 0x4A, 0x2A),
        "text_muted":    (0x6B, 0x56, 0x30),  # canonical base.css value
        "pink_accent":   (0xC4, 0x80, 0x6A),
        "focus_ring":    (0x7A, 0x4A, 0x35),
        "btn_hover_bg":  (0x7A, 0x4A, 0x35),
        "title_override": (0x3D, 0x5A, 0x2E),  # canonical base.css value
        "glass_composite":        (0xED, 0xE4, 0xCE),
        "glass_strong_composite": (0xE5, 0xDB, 0xC4),
        "glass_border_composite": (0xD4, 0xC4, 0xA0),
        "glass_light_composite":  None,
        "_glass_l_rgb": (237, 228, 206), "_glass_l_a": 0.6,
        "_worst_bg":    (0xF5, 0xEF, 0xE0),
    },
    "slate": {
        "bg_light":      (0x1E, 0x1E, 0x1E),
        "bg_mid":        (0x1E, 0x1E, 0x1E),
        "bg_deep":       (0x25, 0x25, 0x25),
        "text_dark":     (0xEC, 0xEC, 0xEC),
        "text_muted":    (0x9A, 0x9A, 0x9A),
        "pink_accent":   (0xD4, 0x71, 0x4E),
        "focus_ring":    (0xD4, 0x71, 0x4E),
        "btn_hover_bg":  (0xA0, 0x45, 0x20),
        "title_override": (0xD4, 0x71, 0x4E),  # matches base.css (.theme-slate .header-title)
        "glass_composite":        (0x25, 0x25, 0x25),
        "glass_strong_composite": (0x38, 0x38, 0x38),
        "glass_border_composite": (0x4A, 0x4A, 0x4A),
        "glass_light_composite":  (0x2D, 0x2D, 0x2D),
    },
}

# Fixed colors used across all themes
WHITE = (255, 255, 255)
KOFI_BG = (0xB9, 0x2D, 0x5D)
DANGER_BG = (0xDC, 0x35, 0x45)

# CSS variable → THEMES key mapping (simple hex-color tokens)
VAR_MAP = {
    "--ls-bg-pink-light": "bg_light",
    "--ls-bg-pink-deep": "bg_deep",
    "--ls-bg-pink": "bg_mid",
    "--ls-text-dark": "text_dark",
    "--ls-text-muted": "text_muted",
    "--ls-pink-accent": "pink_accent",
    "--ls-pink-deep": "pink_deep",
}

# Glass CSS variables → THEMES key mapping (rgba or hex)
# (composite_key_prefix, raw_key_prefix)
GLASS_VAR_MAP = {
    "--ls-glass":        ("glass",        "_glass"),
    "--ls-glass-strong": ("glass_strong", "_glass_s"),
    "--ls-glass-border": ("glass_border", "_glass_b"),
    "--ls-glass-light":  ("glass_light",  "_glass_l"),
}


# ── CSS Parser ─────────────────────────────────────────────────────────────

def parse_hex_color(s):
    """Parse '#RRGGBB' or '#rrggbb' to (R, G, B) tuple."""
    s = s.strip()
    m = re.match(r'^#([0-9a-fA-F]{6})$', s)
    if m:
        h = m.group(1)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    m = re.match(r'^#([0-9a-fA-F]{3})$', s)
    if m:
        h = m.group(1)
        return (int(h[0]*2, 16), int(h[1]*2, 16), int(h[2]*2, 16))
    return None


def parse_rgba_value(s):
    """Parse 'rgba(R, G, B, A)' to ((R, G, B), A)."""
    s = s.strip()
    m = re.match(
        r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)', s
    )
    if m:
        return (
            (int(m.group(1)), int(m.group(2)), int(m.group(3))),
            float(m.group(4)),
        )
    return None


def parse_css_vars(block_text):
    """Extract --ls-* variable declarations from a CSS block body."""
    result = {}
    for m in re.finditer(r'(--ls-[a-z-]+)\s*:\s*([^;]+);', block_text):
        result[m.group(1)] = m.group(2).strip()
    return result


def parse_base_css(path, verbose=False):
    """Parse lovespark-base.css and apply values to THEMES dict.

    Returns the number of tokens overridden, or -1 if file not found.
    """
    if not os.path.exists(path):
        return -1

    with open(path) as f:
        css = f.read()

    # Parse CSS blocks
    parsed_blocks = {}

    # :root block → retro theme
    root_match = re.search(r':root\s*\{([^}]+)\}', css)
    if root_match:
        parsed_blocks["retro"] = parse_css_vars(root_match.group(1))

    # body.theme-{name} blocks
    for theme in ("dark", "beige", "slate"):
        m = re.search(rf'body\.theme-{theme}\s*\{{([^}}]+)\}}', css)
        if m:
            parsed_blocks[theme] = parse_css_vars(m.group(1))

    # Title override selectors
    title_overrides = {}
    for m in re.finditer(
        r'body\.theme-(beige|slate)\s+[^{]*\.header-title[^{]*\{[^}]*'
        r'color:\s*([^;]+);',
        css,
    ):
        color = parse_hex_color(m.group(2))
        if color:
            title_overrides[m.group(1)] = color

    # Apply parsed values to THEMES
    count = 0
    mismatches = []

    for theme_name, vars_dict in parsed_blocks.items():
        if theme_name not in THEMES:
            continue
        t = THEMES[theme_name]

        # Simple hex-color tokens
        for css_var, key in VAR_MAP.items():
            if css_var not in vars_dict:
                continue
            color = parse_hex_color(vars_dict[css_var])
            if color is None:
                continue
            old = t.get(key)
            if old and old != color:
                mismatches.append(
                    f"  {theme_name}.{key}: hardcoded {rgb_hex(old)}"
                    f" -> CSS {rgb_hex(color)}"
                )
            t[key] = color
            count += 1

        # Glass tokens (rgba → compositing data, hex → direct composite)
        for css_var, (comp_prefix, raw_prefix) in GLASS_VAR_MAP.items():
            if css_var not in vars_dict:
                continue
            val = vars_dict[css_var]
            comp_key = f"{comp_prefix}_composite"

            hex_color = parse_hex_color(val)
            if hex_color:
                # Opaque glass — set composite directly
                t[comp_key] = hex_color
                count += 1
                continue

            rgba = parse_rgba_value(val)
            if rgba:
                rgb, alpha = rgba
                t[f"{raw_prefix}_rgb"] = rgb
                t[f"{raw_prefix}_a"] = alpha
                t[comp_key] = None  # recomputed by compute_glass_composites
                count += 1

        # Update _worst_bg from bg_light (lightest gradient point)
        if "bg_light" in t:
            t["_worst_bg"] = t["bg_light"]

    # Title overrides
    for theme_name, color in title_overrides.items():
        if theme_name not in THEMES:
            continue
        old = THEMES[theme_name].get("title_override")
        if old and old != color:
            mismatches.append(
                f"  {theme_name}.title_override: hardcoded {rgb_hex(old)}"
                f" -> CSS {rgb_hex(color)}"
            )
        THEMES[theme_name]["title_override"] = color
        count += 1

    if verbose and mismatches:
        print("--- Token Value Drift (hardcoded vs canonical CSS) ---")
        for m in mismatches:
            print(m)
        print()

    return count


# ── Contrast Math ───────────────────────────────────────────────────────────

def srgb_to_linear(v):
    """Convert sRGB channel (0-255) to linear light value."""
    v = v / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb):
    """WCAG 2.1 relative luminance from (R, G, B) tuple."""
    r, g, b = rgb
    return (0.2126 * srgb_to_linear(r)
            + 0.7152 * srgb_to_linear(g)
            + 0.0722 * srgb_to_linear(b))


def contrast_ratio(fg, bg):
    """WCAG 2.1 contrast ratio between two RGB tuples."""
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def composite_rgba(fg_rgb, fg_alpha, bg_rgb):
    """Composite RGBA foreground on opaque background."""
    return tuple(
        int(fg_alpha * fg_rgb[i] + (1 - fg_alpha) * bg_rgb[i])
        for i in range(3)
    )


def apply_opacity(fg_rgb, opacity, bg_rgb):
    """Apply text opacity (e.g. 0.8) by compositing fg on bg."""
    return composite_rgba(fg_rgb, opacity, bg_rgb)


def rgb_hex(rgb):
    """Format RGB tuple as #RRGGBB."""
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


# ── Compute Glass Composites ────────────────────────────────────────────────

def compute_glass_composites():
    """Pre-compute glass composite colors for themes that use RGBA."""
    for name, t in THEMES.items():
        worst = t.get("_worst_bg")
        if worst is None:
            continue

        if t.get("glass_composite") is None and "_glass_rgb" in t:
            t["glass_composite"] = composite_rgba(
                t["_glass_rgb"], t["_glass_a"], worst
            )

        if t.get("glass_strong_composite") is None and "_glass_s_rgb" in t:
            t["glass_strong_composite"] = composite_rgba(
                t["_glass_s_rgb"], t["_glass_s_a"], worst
            )

        if t.get("glass_border_composite") is None and "_glass_b_rgb" in t:
            t["glass_border_composite"] = composite_rgba(
                t["_glass_b_rgb"], t["_glass_b_a"], worst
            )

        if t.get("glass_light_composite") is None and "_glass_l_rgb" in t:
            t["glass_light_composite"] = composite_rgba(
                t["_glass_l_rgb"], t["_glass_l_a"], worst
            )


# ── Element Checks ──────────────────────────────────────────────────────────

def get_checks(theme_name, t):
    """Return list of (label, fg_rgb, bg_rgb, required_ratio, check_type)."""
    checks = [
        # Body text
        ("Body text on gradient (mid)",
         t["text_dark"], t["bg_mid"], 4.5, "normal"),
        ("Body text on gradient (light)",
         t["text_dark"], t["bg_light"], 4.5, "normal"),
        ("Body text on glass",
         t["text_dark"], t["glass_composite"], 4.5, "normal"),
        ("Body text on glass-strong",
         t["text_dark"], t["glass_strong_composite"], 4.5, "normal"),

        # Muted text
        ("Muted text on glass",
         t["text_muted"], t["glass_composite"], 4.5, "normal"),
        ("Muted text on glass-strong",
         t["text_muted"], t["glass_strong_composite"], 4.5, "normal"),

        # Header/footer text
        ("Header title on bg-light",
         t["text_dark"], t["bg_light"], 4.5, "normal"),
        ("Footer text on bg-deep",
         t["text_dark"], t["bg_deep"], 4.5, "normal"),

        # Hint text (0.8 opacity)
        ("Hint text (0.8 opacity) on glass",
         apply_opacity(t["text_dark"], 0.8, t["glass_composite"]),
         t["glass_composite"], 4.5, "normal"),

        # Button text
        ("White on hover btn",
         WHITE, t["btn_hover_bg"], 4.5, "normal"),
        ("White on accent btn",
         WHITE, t["pink_accent"], 4.5, "normal"),
        ("White on Ko-fi btn",
         WHITE, KOFI_BG, 4.5, "normal"),
        ("White on danger btn",
         WHITE, DANGER_BG, 4.5, "normal"),

        # Dropdown
        ("Dropdown header on glass-strong",
         t["text_dark"], t["glass_strong_composite"], 4.5, "normal"),
        ("Dropdown option on glass-strong",
         t["text_dark"], t["glass_strong_composite"], 4.5, "normal"),

        # UI components (3:1)
        ("Focus ring on bg-light",
         t["focus_ring"], t["bg_light"], 3.0, "ui"),
        ("Focus ring on glass",
         t["focus_ring"], t["glass_composite"], 3.0, "ui"),
        ("Toggle active on glass",
         t["focus_ring"], t["glass_composite"], 3.0, "ui"),
        ("Slider thumb on track",
         t["focus_ring"], t["glass_border_composite"], 3.0, "ui"),
    ]

    # Theme-specific title overrides
    if theme_name == "beige" and "title_override" in t:
        checks.append((
            "Beige title override on bg",
            t["title_override"], t["bg_light"], 4.5, "normal"
        ))
        checks.append((
            "Beige title override on glass",
            t["title_override"], t["glass_composite"], 4.5, "normal"
        ))

    if theme_name == "slate" and "title_override" in t:
        checks.append((
            "Slate title override on bg",
            t["title_override"], t["bg_light"], 4.5, "normal"
        ))
        checks.append((
            "Slate title override on glass",
            t["title_override"], t["glass_composite"], 4.5, "normal"
        ))

    return checks


# ── History & Regression Detection ──────────────────────────────────────────

HISTORY_PATH = os.path.expanduser(
    "~/.claude/docs/memory/contrast-history.json"
)


def load_history():
    """Load previous audit results for regression detection."""
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH) as f:
            return json.load(f)
    return {"runs": []}


def save_history(all_results, total_pass, total_fail, source):
    """Save current run to history file."""
    history = load_history()

    snapshot = {
        "date": date.today().isoformat(),
        "source": source,
        "total_pass": total_pass,
        "total_fail": total_fail,
        "failures": {},
    }
    for theme_name, results in all_results.items():
        fails = [r["label"] for r in results if not r["pass"]]
        if fails:
            snapshot["failures"][theme_name] = fails

    history["runs"].append(snapshot)
    history["runs"] = history["runs"][-20:]

    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)


def check_regressions(all_results):
    """Compare against last run and report regressions."""
    history = load_history()
    if not history["runs"]:
        return []

    last = history["runs"][-1]
    last_failures = set()
    for theme, labels in last.get("failures", {}).items():
        for label in labels:
            last_failures.add(f"{theme}:{label}")

    regressions = []
    for theme_name, results in all_results.items():
        for r in results:
            key = f"{theme_name}:{r['label']}"
            if not r["pass"] and key not in last_failures:
                regressions.append({
                    "theme": theme_name,
                    "label": r["label"],
                    "ratio": r["ratio"],
                    "required": r["required"],
                })

    return regressions


def main():
    parser = argparse.ArgumentParser(
        description="LoveSpark WCAG 2.1 contrast auditor for all 4 themes"
    )
    parser.add_argument(
        "--theme",
        choices=list(THEMES.keys()),
        help="Audit a single theme (default: all)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show PASS results and token drift warnings",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Save results and detect regressions against last run",
    )
    parser.add_argument(
        "--css",
        default=CSS_FILE,
        help="Path to lovespark-base.css (default: canonical shared lib)",
    )
    parser.add_argument(
        "--hardcoded",
        action="store_true",
        help="Skip CSS parsing, use hardcoded fallback values only",
    )
    args = parser.parse_args()

    # Parse CSS unless --hardcoded
    source = "hardcoded"
    if not args.hardcoded:
        n = parse_base_css(args.css, verbose=args.verbose)
        if n == -1:
            if not args.json:
                print(f"  CSS file not found: {args.css}")
                print("  Using hardcoded fallback values.\n")
        else:
            source = f"css:{os.path.basename(args.css)}"
            if not args.json:
                print(f"  Loaded {n} token(s) from {args.css}\n")

    compute_glass_composites()

    themes_to_check = (
        {args.theme: THEMES[args.theme]}
        if args.theme
        else THEMES
    )

    all_results = {}
    total_pass = 0
    total_fail = 0

    for theme_name, t in themes_to_check.items():
        checks = get_checks(theme_name, t)
        results = []

        for label, fg, bg, required, check_type in checks:
            ratio = contrast_ratio(fg, bg)
            passed = ratio >= required
            results.append({
                "label": label,
                "fg": rgb_hex(fg),
                "bg": rgb_hex(bg),
                "ratio": round(ratio, 2),
                "required": required,
                "type": check_type,
                "pass": passed,
            })
            if passed:
                total_pass += 1
            else:
                total_fail += 1

        all_results[theme_name] = results

    # Regression detection
    regressions = []
    if args.history:
        regressions = check_regressions(all_results)

    if args.json:
        output = {
            "source": source,
            "themes": all_results,
            "summary": {
                "total_pass": total_pass,
                "total_fail": total_fail,
                "exit_code": 0 if total_fail == 0 else 1,
            },
        }
        if regressions:
            output["regressions"] = regressions
        print(json.dumps(output, indent=2))
    else:
        print("=== LoveSpark Contrast Audit ===\n")

        for theme_name, results in all_results.items():
            theme_pass = sum(1 for r in results if r["pass"])
            theme_total = len(results)
            print(f"--- {theme_name.capitalize()} ---")

            for r in results:
                if r["pass"] and not args.verbose:
                    continue
                status = " PASS" if r["pass"] else " FAIL"
                req_label = f"needs {r['required']}:1"
                print(
                    f"  {status}  {r['label']:<40} "
                    f"{r['fg']} on {r['bg']}  "
                    f"{r['ratio']}:1 ({req_label})"
                )

            print(f"  {theme_pass}/{theme_total} pass\n")

        # Regressions
        if regressions:
            print("!!! REGRESSIONS DETECTED !!!")
            for reg in regressions:
                print(
                    f"  NEW FAIL  [{reg['theme']}] {reg['label']}  "
                    f"{reg['ratio']}:1 (needs {reg['required']}:1)"
                )
            print(f"  {len(regressions)} new failure(s) since last run\n")

        # Summary
        print("--- Summary ---")
        print(f"  Source: {source}")
        for theme_name, results in all_results.items():
            theme_pass = sum(1 for r in results if r["pass"])
            theme_total = len(results)
            print(
                f"  {theme_name.capitalize()}: "
                f"{theme_pass}/{theme_total} pass",
                end="",
            )
            if theme_pass < theme_total:
                print(f" | {theme_total - theme_pass} FAILURES", end="")
            print()

        if total_fail > 0:
            print(f"\n  {total_fail} failure(s). Exit code: 1")
        else:
            print(f"\n  All {total_pass} checks pass. Exit code: 0")

    # Save history
    if args.history:
        save_history(all_results, total_pass, total_fail, source)
        if not args.json:
            print(f"\n  History saved to {HISTORY_PATH}")

    sys.exit(1 if total_fail > 0 else 0)


if __name__ == "__main__":
    main()
