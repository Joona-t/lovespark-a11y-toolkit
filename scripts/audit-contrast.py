#!/usr/bin/env python3
"""LoveSpark Contrast Audit — WCAG 2.1 contrast checker for all 4 themes.

Zero external dependencies. Uses relative luminance formula per WCAG 2.1.
Data-oriented: theme colors and element mappings as flat dicts, no CSS parsing.

Features:
  --history: Save results and detect regressions between runs
  Persistent history at ~/.claude/docs/memory/contrast-history.json

Usage:
    python3 audit-contrast.py [--theme THEME] [--verbose] [--json] [--history]
"""

import argparse
import json
import os
import sys
from datetime import date

# ── Theme Palettes ──────────────────────────────────────────────────────────
# Token values from canonical lovespark-base.css + cozy-accessibility popup.css
# Glass composites are pre-computed using worst-case (lightest) gradient point.

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
        # Glass composites on worst-case bg (#FDCFE1)
        # glass rgba(255,255,255,0.45) on (253,207,225)
        "glass_composite":        None,  # computed below
        "glass_strong_composite": None,
        "glass_border_composite": None,
        "glass_light_composite":  None,
        # Raw glass values for compositing
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
        "text_muted":    (0x6B, 0x56, 0x30),
        "pink_accent":   (0xC4, 0x80, 0x6A),
        "focus_ring":    (0x7A, 0x4A, 0x35),
        "btn_hover_bg":  (0x7A, 0x4A, 0x35),
        "title_override": (0x3D, 0x5A, 0x2E),
        # Beige uses opaque glass values — no compositing needed
        "glass_composite":        (0xED, 0xE4, 0xCE),
        "glass_strong_composite": (0xE5, 0xDB, 0xC4),
        "glass_border_composite": (0xD4, 0xC4, 0xA0),
        "glass_light_composite":  None,  # rgba — needs compositing
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
        "title_override": (0xE8, 0x92, 0x6E),
        # Slate uses opaque glass values
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


# ── Contrast Math ───────────────────────────────────────────────────────────

def srgb_to_linear(v):
    """Convert sRGB channel (0-255) to linear light value."""
    v = v / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb):
    """WCAG 2.1 relative luminance from (R, G, B) tuple."""
    r, g, b = rgb
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)


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


def save_history(all_results, total_pass, total_fail):
    """Save current run to history file."""
    history = load_history()

    # Build compact snapshot
    snapshot = {
        "date": date.today().isoformat(),
        "total_pass": total_pass,
        "total_fail": total_fail,
        "failures": {},
    }
    for theme_name, results in all_results.items():
        fails = [r["label"] for r in results if not r["pass"]]
        if fails:
            snapshot["failures"][theme_name] = fails

    # Keep last 20 runs
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
        help="Show PASS results too (default: FAIL only)",
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
    args = parser.parse_args()

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
        for theme_name, results in all_results.items():
            theme_pass = sum(1 for r in results if r["pass"])
            theme_total = len(results)
            print(f"  {theme_name.capitalize()}: {theme_pass}/{theme_total} pass", end="")
            if theme_pass < theme_total:
                print(f" | {theme_total - theme_pass} FAILURES", end="")
            print()

        if total_fail > 0:
            print(f"\n  {total_fail} failure(s). Exit code: 1")
        else:
            print(f"\n  All {total_pass} checks pass. Exit code: 0")

    # Save history
    if args.history:
        save_history(all_results, total_pass, total_fail)
        if not args.json:
            print(f"\n  History saved to {HISTORY_PATH}")

    sys.exit(1 if total_fail > 0 else 0)


if __name__ == "__main__":
    main()
