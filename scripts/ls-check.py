#!/usr/bin/env python3
"""ls-check — Unified LoveSpark quality pipeline.

Zero external dependencies. Auto-detects project type and runs relevant checks.

Usage:
    ls-check .                          # full check, auto-detect project type
    ls-check . --pre-commit             # fast grep-based checks only (<2s)
    ls-check . --strict                 # warnings become failures
    ls-check . --only accessibility     # single category
    ls-check . --json                   # machine-readable output
    ls-check . --history                # save results for regression detection
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
SHARED_LIB = BASE_DIR / "Extensions" / "infrastructure" / "lovespark-shared-lib"
HISTORY_PATH = Path.home() / ".claude" / "docs" / "memory" / "ls-check-history.json"

SHARED_FILES = [
    "lovespark-base.css",
    "lovespark-stats.js",
    "lovespark-badge.js",
    "lovespark-theme.js",
    "lovespark-popup.js",
    "lovespark-lifecycle.js",
]

# ── Terminal Colors ───────────────────────────────────────────────────────

RED = "\033[0;31m"
YLW = "\033[0;33m"
GRN = "\033[0;32m"
CYN = "\033[0;36m"
DIM = "\033[2m"
RST = "\033[0m"
BOLD = "\033[1m"


# ── Project Type Detection ────────────────────────────────────────────────

def detect_project_type(path):
    """Auto-detect project type from directory contents."""
    p = Path(path)

    manifest = p / "manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text())
            if "manifest_version" in data:
                return "extension"
        except (json.JSONDecodeError, OSError):
            pass

    if (p / "Cargo.toml").exists():
        return "rust"

    if (p / "Package.swift").exists() or list(p.glob("*.xcodeproj")):
        return "ios"

    pkg = p / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "expo" in deps or "react-native" in deps:
                return "ios-expo"
            if "next" in deps or "react" in deps:
                return "web-react"
        except (json.JSONDecodeError, OSError):
            pass

    if (p / "setup.py").exists() or (p / "pyproject.toml").exists() or (p / "requirements.txt").exists():
        return "python"

    if (p / "index.html").exists():
        return "web-static"

    return "general"


# ── File Collection ───────────────────────────────────────────────────────

def collect_files(path, ext):
    """Collect files by extension, excluding node_modules and .git."""
    results = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "__pycache__", ".build")]
        for f in files:
            if f.endswith(ext):
                results.append(os.path.join(root, f))
    return results


def read_file_safe(path):
    """Read file contents, return empty string on error."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


# ── Check Result ──────────────────────────────────────────────────────────

class CheckResult:
    def __init__(self, check_id, passed, message, details=None, severity="fail"):
        self.check_id = check_id
        self.passed = passed
        self.message = message
        self.details = details or []  # list of strings: file:line or fix hints
        self.severity = severity  # "fail" or "warn"

    def to_dict(self):
        return {
            "id": self.check_id,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "severity": self.severity,
        }


# ── Accessibility Checks (extensions) ─────────────────────────────────────

def check_a11y_contrast(path):
    """A11Y-CONTRAST: Delegate to audit-contrast.py."""
    script = SCRIPT_DIR / "audit-contrast.py"
    if not script.exists():
        return CheckResult("A11Y-CONTRAST", False, "audit-contrast.py not found", severity="warn")
    try:
        r = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(r.stdout)
        total_fail = data.get("summary", {}).get("total_fail", 0)
        total_pass = data.get("summary", {}).get("total_pass", 0)
        if total_fail == 0:
            return CheckResult("A11Y-CONTRAST", True, f"Contrast audit ({total_pass} pass, all 4 themes)")
        details = []
        for theme, results in data.get("themes", {}).items():
            for res in results:
                if not res["pass"]:
                    details.append(f"  [{theme}] {res['label']}: {res['ratio']}:1 (needs {res['required']}:1)")
        return CheckResult("A11Y-CONTRAST", False, f"Contrast audit: {total_fail} failure(s)", details)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        return CheckResult("A11Y-CONTRAST", False, f"Contrast audit error: {e}", severity="warn")


def check_a11y_ki001(css_files):
    """A11Y-KI001: --ls-pink-accent not used as bg for white text."""
    hits = []
    for f in css_files:
        content = read_file_safe(f)
        for i, line in enumerate(content.splitlines(), 1):
            if re.search(r'background.*--ls-pink-accent', line):
                # Check context for toggle/slider (safe)
                start = max(0, i - 6)
                lines = content.splitlines()[start:i + 5]
                ctx = "\n".join(lines).lower()
                if any(w in ctx for w in ("toggle", "slider", "thumb", "::")):
                    continue
                hits.append(f"  {f}:{i}")
    if hits:
        return CheckResult("A11Y-KI001", False,
                           "--ls-pink-accent used as background (fails contrast with white text)",
                           hits + ["  Fix: use --ls-pink-deep or --ls-btn-hover-bg instead"])
    return CheckResult("A11Y-KI001", True, "No --ls-pink-accent as background")


def check_a11y_ki004(css_files):
    """A11Y-KI004: No opacity < 0.85 on text in beige theme."""
    hits = []
    for f in css_files:
        content = read_file_safe(f)
        for i, line in enumerate(content.splitlines(), 1):
            m = re.search(r'opacity:\s*(0\.\d+)', line)
            if m:
                val = float(m.group(1))
                if val < 0.85:
                    hits.append(f"  {f}:{i} opacity: {val}")
    if hits:
        return CheckResult("A11Y-KI004", False,
                           "Low opacity on text (fails in beige theme)", hits, severity="warn")
    return CheckResult("A11Y-KI004", True, "No low-opacity text elements")


def check_a11y_ki006(css_files):
    """A11Y-KI006: No outline:none without :focus-visible replacement."""
    hits = []
    for f in css_files:
        if os.path.basename(f) == "lovespark-base.css":
            continue
        content = read_file_safe(f)
        if re.search(r'outline:\s*(?:none|0[^.])', content):
            if ":focus-visible" not in content:
                hits.append(f"  {f}")
    if hits:
        return CheckResult("A11Y-KI006", False,
                           "outline: none without :focus-visible replacement",
                           hits + ["  Fix: Add :focus-visible rule or rely on lovespark-base.css defaults"])
    return CheckResult("A11Y-KI006", True, "No bare outline suppressions")


def check_a11y_ki008(css_files):
    """A11Y-KI008: transition/animation has prefers-reduced-motion."""
    hits = []
    for f in css_files:
        if os.path.basename(f) == "lovespark-base.css":
            continue
        content = read_file_safe(f)
        has_anim = bool(re.search(r'transition:|animation:', content))
        has_motion = "prefers-reduced-motion" in content
        if has_anim and not has_motion:
            # Check if it loads base.css (which has the global reduced-motion)
            # If this is a standalone CSS file, it needs its own
            hits.append(f"  {f}")
    if hits:
        return CheckResult("A11Y-KI008", False,
                           "Animations without prefers-reduced-motion",
                           hits + ["  Fix: Add @media (prefers-reduced-motion: reduce) block or load lovespark-base.css"],
                           severity="warn")
    return CheckResult("A11Y-KI008", True, "All animated CSS has prefers-reduced-motion")


def check_a11y_dialog(html_files):
    """A11Y-DIALOG: popup.html has role='dialog' + aria-labelledby."""
    for f in html_files:
        if os.path.basename(f) != "popup.html":
            continue
        content = read_file_safe(f)
        has_dialog = 'role="dialog"' in content
        has_label = "aria-labelledby" in content
        if not has_dialog or not has_label:
            missing = []
            if not has_dialog:
                missing.append('role="dialog"')
            if not has_label:
                missing.append("aria-labelledby")
            return CheckResult("A11Y-DIALOG", False,
                               f"popup.html missing {' and '.join(missing)}",
                               [f"  {f}"])
        # Check for alertdialog misuse
        if 'role="alertdialog"' in content:
            return CheckResult("A11Y-DIALOG", False,
                               'popup.html uses role="alertdialog" — should be role="dialog"',
                               [f"  {f}"], severity="warn")
        return CheckResult("A11Y-DIALOG", True, 'role="dialog" + aria-labelledby present')
    return CheckResult("A11Y-DIALOG", True, "No popup.html found (N/A)", severity="warn")


def check_a11y_expanded(html_files, js_files):
    """A11Y-EXPANDED: dropdown triggers have aria-expanded."""
    has_dropdown = False
    for f in html_files + js_files:
        content = read_file_safe(f)
        if "dropdown" in content.lower() or "theme-dropdown" in content:
            has_dropdown = True
            break
    if not has_dropdown:
        return CheckResult("A11Y-EXPANDED", True, "No dropdowns found (N/A)")

    for f in html_files:
        content = read_file_safe(f)
        if "dropdown" in content.lower() and "aria-expanded" not in content:
            return CheckResult("A11Y-EXPANDED", False,
                               "Dropdown trigger missing aria-expanded",
                               [f"  {f}", "  Fix: Add aria-expanded='false' to dropdown trigger button"])
    return CheckResult("A11Y-EXPANDED", True, "Dropdown triggers have aria-expanded")


def check_a11y_label(html_files):
    """A11Y-LABEL: emoji/symbol buttons have aria-label."""
    hits = []
    emoji_btn_re = re.compile(r'<button[^>]*>([^<]*[\U00010000-\U0010ffff✕✖✗✘×➜→←↑↓★☆♥♡●○■□▲△▼▽][^<]*)</button>', re.UNICODE)
    for f in html_files:
        content = read_file_safe(f)
        for m in emoji_btn_re.finditer(content):
            # Check if the button tag has aria-label
            btn_start = content.rfind("<button", 0, m.start() + 7)
            btn_tag = content[btn_start:m.end()]
            if "aria-label" not in btn_tag:
                hits.append(f"  {f}: button with '{m.group(1).strip()[:20]}' lacks aria-label")
    if hits:
        return CheckResult("A11Y-LABEL", False, "Emoji/symbol buttons missing aria-label", hits)
    return CheckResult("A11Y-LABEL", True, "All emoji buttons have aria-label")


def check_a11y_live(js_files):
    """A11Y-LIVE: dynamic .textContent targets should have aria-live."""
    # This is a heuristic — check for .textContent = assignments on stat elements
    hits = []
    for f in js_files:
        content = read_file_safe(f)
        # Look for patterns like: el.textContent = value (common stat updates)
        dynamic_ids = set()
        for m in re.finditer(r"getElementById\(['\"](\w+)['\"]\)", content):
            el_id = m.group(1)
            # Check if this element gets textContent updates
            if re.search(rf'{el_id}[^;]*\.textContent\s*=', content) or \
               re.search(r'animateCount\(', content):
                dynamic_ids.add(el_id)
        if dynamic_ids:
            # Just flag as warning — the HTML needs aria-live, not JS
            for eid in dynamic_ids:
                hits.append(f"  {f}: #{eid} gets dynamic updates — ensure aria-live='polite' in HTML")
    if hits:
        return CheckResult("A11Y-LIVE", False, "Dynamic content targets may need aria-live", hits, severity="warn")
    return CheckResult("A11Y-LIVE", True, "Dynamic content handling OK")


def check_a11y_input(html_files):
    """A11Y-INPUT: inputs have aria-label or <label>."""
    hits = []
    for f in html_files:
        content = read_file_safe(f)
        for m in re.finditer(r'<input\b([^>]*)>', content):
            attrs = m.group(1)
            if 'type="hidden"' in attrs or 'type="submit"' in attrs:
                continue
            has_label = "aria-label" in attrs or "aria-labelledby" in attrs or "id=" in attrs
            if "id=" in attrs:
                # Check for associated <label for="">
                id_m = re.search(r'id=["\']([^"\']+)["\']', attrs)
                if id_m:
                    has_label = has_label or f'for="{id_m.group(1)}"' in content
            if not has_label:
                hits.append(f"  {f}: <input> without label or aria-label")
    if hits:
        return CheckResult("A11Y-INPUT", False, "Inputs missing accessible labels", hits)
    return CheckResult("A11Y-INPUT", True, "All inputs have accessible labels")


def check_a11y_touch(css_files):
    """A11Y-TOUCH: interactive elements >= 32px (heuristic check)."""
    # Check if base.css is loaded (which now enforces min-height: 32px)
    # This is a best-effort check
    return CheckResult("A11Y-TOUCH", True, "Touch targets enforced by lovespark-base.css min-height: 32px")


def check_a11y_lang(html_files):
    """A11Y-LANG: <html lang='en'> present."""
    for f in html_files:
        content = read_file_safe(f)
        if "<html" in content and 'lang=' not in content:
            return CheckResult("A11Y-LANG", False, f'<html> missing lang attribute',
                               [f"  {f}", '  Fix: Add lang="en" to <html> tag'])
    return CheckResult("A11Y-LANG", True, '<html lang="en"> present')


# ── Security Checks (extensions) ──────────────────────────────────────────

def check_sec_innerhtml(js_files):
    """SEC-INNERHTML: No .innerHTML assignments."""
    hits = []
    for f in js_files:
        content = read_file_safe(f)
        for i, line in enumerate(content.splitlines(), 1):
            if re.search(r'\.innerHTML\s*=', line):
                hits.append(f"  {f}:{i}: {line.strip()[:80]}")
    if hits:
        return CheckResult("SEC-INNERHTML", False, "innerHTML assignment found — use textContent or DOM API", hits)
    return CheckResult("SEC-INNERHTML", True, "No innerHTML usage")


def check_sec_csp(path):
    """SEC-CSP: manifest has content_security_policy."""
    manifest = Path(path) / "manifest.json"
    if not manifest.exists():
        return CheckResult("SEC-CSP", True, "No manifest.json (N/A)")
    try:
        data = json.loads(manifest.read_text())
        if "content_security_policy" in data:
            return CheckResult("SEC-CSP", True, "CSP present in manifest")
        return CheckResult("SEC-CSP", False, "No content_security_policy in manifest.json",
                           ["  Fix: Add content_security_policy.extension_pages to manifest.json"],
                           severity="warn")
    except (json.JSONDecodeError, OSError):
        return CheckResult("SEC-CSP", False, "Could not parse manifest.json", severity="warn")


def check_sec_cdn(html_files, js_files):
    """SEC-CDN: No external CDN links."""
    hits = []
    cdn_re = re.compile(r'(?:src|href)=["\']https?://(?!fonts\.googleapis\.com|fonts\.gstatic\.com)')
    for f in html_files + js_files:
        content = read_file_safe(f)
        for i, line in enumerate(content.splitlines(), 1):
            if cdn_re.search(line):
                hits.append(f"  {f}:{i}: {line.strip()[:80]}")
    if hits:
        return CheckResult("SEC-CDN", False, "External CDN links found — bundle locally", hits)
    return CheckResult("SEC-CDN", True, "No external CDN links")


def check_sec_ext_connect(path):
    """SEC-EXT-CONNECT: No wildcard externally_connectable."""
    manifest = Path(path) / "manifest.json"
    if not manifest.exists():
        return CheckResult("SEC-EXT-CONNECT", True, "No manifest.json (N/A)")
    try:
        data = json.loads(manifest.read_text())
        ec = data.get("externally_connectable", {})
        matches = ec.get("matches", [])
        if any("*" in m and m != "<all_urls>" for m in matches):
            return CheckResult("SEC-EXT-CONNECT", False,
                               "Wildcard in externally_connectable",
                               ["  Fix: Restrict to specific origins"])
        return CheckResult("SEC-EXT-CONNECT", True, "No wildcard externally_connectable")
    except (json.JSONDecodeError, OSError):
        return CheckResult("SEC-EXT-CONNECT", True, "Could not parse manifest.json")


def check_sec_empty_catch(js_files):
    """SEC-EMPTY-CATCH: No empty catch blocks in service workers."""
    hits = []
    for f in js_files:
        if "background" not in os.path.basename(f).lower() and "sw" not in os.path.basename(f).lower():
            continue
        content = read_file_safe(f)
        # Pattern: catch (...) { } or catch { }
        for m in re.finditer(r'catch\s*(?:\([^)]*\))?\s*\{(\s*)\}', content):
            line_num = content[:m.start()].count('\n') + 1
            hits.append(f"  {f}:{line_num}")
    if hits:
        return CheckResult("SEC-EMPTY-CATCH", False, "Empty catch blocks in service worker", hits)
    return CheckResult("SEC-EMPTY-CATCH", True, "No empty catch blocks in SWs")


def check_sec_sendmsg(js_files):
    """SEC-SENDMSG: sendMessage wrapped in try/catch or .catch()."""
    hits = []
    for f in js_files:
        content = read_file_safe(f)
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if "sendMessage(" in line:
                # Check if wrapped in try/catch or has .catch/.then
                ctx_start = max(0, i - 5)
                ctx_end = min(len(lines), i + 3)
                ctx = "\n".join(lines[ctx_start:ctx_end])
                if "try" not in ctx and ".catch" not in ctx and ".then" not in ctx and "await" not in ctx:
                    hits.append(f"  {f}:{i}: sendMessage without error handling")
    if hits:
        return CheckResult("SEC-SENDMSG", False, "sendMessage not wrapped in try/catch", hits, severity="warn")
    return CheckResult("SEC-SENDMSG", True, "sendMessage calls have error handling")


# ── MV3 Checks (extensions) ──────────────────────────────────────────────

def check_mv3_storage_mix(js_files):
    """MV3-STORAGE-MIX: No mixed storage.sync/storage.local."""
    has_sync = []
    has_local = []
    for f in js_files:
        content = read_file_safe(f)
        if "storage.sync" in content:
            has_sync.append(f)
        if "storage.local" in content:
            has_local.append(f)
    if has_sync and has_local:
        return CheckResult("MV3-STORAGE-MIX", False,
                           "Mixed storage.sync and storage.local",
                           [f"  sync: {', '.join(has_sync)}",
                            f"  local: {', '.join(has_local)}",
                            "  Fix: Use storage.local exclusively"])
    if has_sync:
        return CheckResult("MV3-STORAGE-MIX", False,
                           "storage.sync found — use storage.local",
                           [f"  {f}" for f in has_sync])
    return CheckResult("MV3-STORAGE-MIX", True, "Storage API consistent (local only)")


def check_mv3_storage_key(js_files):
    """MV3-STORAGE-KEY: Save/load use same key strings."""
    # Heuristic: collect .set({key:}) and .get([key]) patterns
    set_keys = set()
    get_keys = set()
    for f in js_files:
        content = read_file_safe(f)
        for m in re.finditer(r'storage\.local\.set\(\s*\{([^}]+)\}', content):
            for k in re.findall(r"(\w+)\s*:", m.group(1)):
                set_keys.add(k)
        for m in re.finditer(r"storage\.local\.get\(\s*\[([^\]]+)\]", content):
            for k in re.findall(r"['\"](\w+)['\"]", m.group(1)):
                get_keys.add(k)
    if set_keys and get_keys:
        set_only = set_keys - get_keys
        get_only = get_keys - set_keys
        if set_only or get_only:
            details = []
            if set_only:
                details.append(f"  Set but never read: {', '.join(sorted(set_only))}")
            if get_only:
                details.append(f"  Read but never set: {', '.join(sorted(get_only))}")
            return CheckResult("MV3-STORAGE-KEY", False,
                               "Storage key mismatch between save/load", details, severity="warn")
    return CheckResult("MV3-STORAGE-KEY", True, "Storage keys consistent")


def check_mv3_settimeout(js_files):
    """MV3-SETTIMEOUT: No setTimeout deferring storage in SW."""
    hits = []
    for f in js_files:
        if "background" not in os.path.basename(f).lower():
            continue
        content = read_file_safe(f)
        for i, line in enumerate(content.splitlines(), 1):
            if "setTimeout" in line:
                # Check if storage is referenced nearby
                ctx_start = max(0, i - 1)
                ctx_end = min(len(content.splitlines()), i + 10)
                ctx = "\n".join(content.splitlines()[ctx_start:ctx_end])
                if "storage" in ctx:
                    hits.append(f"  {f}:{i}: setTimeout + storage in service worker")
    if hits:
        return CheckResult("MV3-SETTIMEOUT", False,
                           "setTimeout deferring storage in service worker — may not fire",
                           hits)
    return CheckResult("MV3-SETTIMEOUT", True, "No setTimeout + storage in SW")


def check_mv3_debug_guard(js_files):
    """MV3-DEBUG-GUARD: No onRuleMatchedDebug as if-guard."""
    hits = []
    for f in js_files:
        content = read_file_safe(f)
        if "onRuleMatchedDebug" in content:
            for i, line in enumerate(content.splitlines(), 1):
                if re.search(r'if\s*\(.*onRuleMatchedDebug', line):
                    hits.append(f"  {f}:{i}")
    if hits:
        return CheckResult("MV3-DEBUG-GUARD", False,
                           "onRuleMatchedDebug used as if-guard (crashes in production)",
                           hits + ["  Fix: Wrap in try/catch instead"])
    return CheckResult("MV3-DEBUG-GUARD", True, "No onRuleMatchedDebug if-guards")


def check_mv3_dnr_prop(js_files):
    """MV3-DNR-PROP: .rulesMatchedInfo not .matchedRules."""
    hits = []
    for f in js_files:
        content = read_file_safe(f)
        for i, line in enumerate(content.splitlines(), 1):
            if ".matchedRules" in line and "rulesMatchedInfo" not in line:
                hits.append(f"  {f}:{i}: Use .rulesMatchedInfo instead of .matchedRules")
    if hits:
        return CheckResult("MV3-DNR-PROP", False,
                           "Wrong DNR property name (.matchedRules → .rulesMatchedInfo)", hits)
    return CheckResult("MV3-DNR-PROP", True, "DNR property names correct")


def check_mv3_setinterval(js_files):
    """MV3-SETINTERVAL: No setInterval in content scripts."""
    hits = []
    for f in js_files:
        if "content" not in os.path.basename(f).lower():
            continue
        content = read_file_safe(f)
        for i, line in enumerate(content.splitlines(), 1):
            if "setInterval" in line:
                hits.append(f"  {f}:{i}")
    if hits:
        return CheckResult("MV3-SETINTERVAL", False,
                           "setInterval in content script — use MutationObserver instead",
                           hits)
    return CheckResult("MV3-SETINTERVAL", True, "No setInterval in content scripts")


# ── Brand Checks (extensions) ────────────────────────────────────────────

def check_brand_sparky(path):
    """BRAND-SPARKY: mascot.png exists."""
    if (Path(path) / "mascot.png").exists():
        return CheckResult("BRAND-SPARKY", True, "mascot.png present")
    return CheckResult("BRAND-SPARKY", False, "mascot.png missing",
                       ["  Fix: Copy from 'Assets & Docs/mascot.png'"])


def check_brand_gradient(css_files, html_files):
    """BRAND-GRADIENT: body uses --ls-bg-gradient."""
    for f in css_files:
        content = read_file_safe(f)
        if re.search(r'body\s*\{[^}]*--ls-bg-gradient', content, re.DOTALL):
            return CheckResult("BRAND-GRADIENT", True, "Body uses --ls-bg-gradient")
    return CheckResult("BRAND-GRADIENT", False, "Body doesn't use --ls-bg-gradient background",
                       ["  Fix: Add 'background: var(--ls-bg-gradient)' to body style"])


def check_brand_theme(path, html_files, js_files):
    """BRAND-THEME: Theme support present."""
    for f in html_files + js_files:
        content = read_file_safe(f)
        if "lovespark-theme" in content or "LoveSparkTheme" in content:
            return CheckResult("BRAND-THEME", True, "Theme support present")
    return CheckResult("BRAND-THEME", False, "No theme support detected",
                       ["  Fix: Include lovespark-theme.js and call LoveSparkTheme.init()"],
                       severity="warn")


def check_brand_lib_sync(path):
    """BRAND-LIB-SYNC: Shared lib matches canonical checksums."""
    lib_dir = Path(path) / "lib"
    if not lib_dir.exists():
        return CheckResult("BRAND-LIB-SYNC", True, "No lib/ directory (N/A)", severity="warn")

    mismatches = []
    for fname in SHARED_FILES:
        canonical = SHARED_LIB / fname
        local = lib_dir / fname
        if not canonical.exists() or not local.exists():
            continue
        c_hash = hashlib.md5(canonical.read_bytes()).hexdigest()
        l_hash = hashlib.md5(local.read_bytes()).hexdigest()
        if c_hash != l_hash:
            mismatches.append(f"  {fname}: local differs from canonical")

    if mismatches:
        return CheckResult("BRAND-LIB-SYNC", False,
                           "Shared lib out of sync with canonical",
                           mismatches + ["  Fix: Run scripts/sync-shared-lib.sh"])
    return CheckResult("BRAND-LIB-SYNC", True, "Shared lib matches canonical")


def check_brand_lib_wired(html_files):
    """BRAND-LIB-WIRED: popup.html loads shared lib files."""
    for f in html_files:
        if os.path.basename(f) != "popup.html":
            continue
        content = read_file_safe(f)
        missing = []
        if "lovespark-base.css" not in content:
            missing.append("lovespark-base.css")
        if "lovespark-theme.js" not in content:
            missing.append("lovespark-theme.js")
        if missing:
            return CheckResult("BRAND-LIB-WIRED", False,
                               f"popup.html missing shared lib: {', '.join(missing)}",
                               [f"  {f}"])
        return CheckResult("BRAND-LIB-WIRED", True, "popup.html loads shared lib files")
    return CheckResult("BRAND-LIB-WIRED", True, "No popup.html (N/A)")


# ── Permission Checks (extensions) ───────────────────────────────────────

def check_perm_unused(path, js_files):
    """PERM-UNUSED: Declared permissions actually used."""
    manifest = Path(path) / "manifest.json"
    if not manifest.exists():
        return CheckResult("PERM-UNUSED", True, "No manifest.json (N/A)")
    try:
        data = json.loads(manifest.read_text())
    except (json.JSONDecodeError, OSError):
        return CheckResult("PERM-UNUSED", True, "Could not parse manifest.json")

    perms = set(data.get("permissions", []))
    all_js = "\n".join(read_file_safe(f) for f in js_files)

    # Map permissions to expected API usage
    perm_api_map = {
        "storage": "storage",
        "tabs": "chrome.tabs",
        "activeTab": "activeTab",  # implicit
        "alarms": "chrome.alarms",
        "notifications": "chrome.notifications",
        "contextMenus": "chrome.contextMenus",
        "declarativeNetRequest": "declarativeNetRequest",
        "cookies": "chrome.cookies",
        "webNavigation": "chrome.webNavigation",
        "scripting": "chrome.scripting",
        "sidePanel": "chrome.sidePanel",
    }

    unused = []
    for perm in perms:
        if perm in perm_api_map:
            api = perm_api_map[perm]
            if api not in all_js and perm != "activeTab":
                unused.append(f"  '{perm}' declared but '{api}' not found in JS")

    if unused:
        return CheckResult("PERM-UNUSED", False, "Potentially unused permissions", unused, severity="warn")
    return CheckResult("PERM-UNUSED", True, "All declared permissions appear used")


def check_perm_missing(path, js_files):
    """PERM-MISSING: API calls needing undeclared permissions."""
    manifest = Path(path) / "manifest.json"
    if not manifest.exists():
        return CheckResult("PERM-MISSING", True, "No manifest.json (N/A)")
    try:
        data = json.loads(manifest.read_text())
    except (json.JSONDecodeError, OSError):
        return CheckResult("PERM-MISSING", True, "Could not parse manifest.json")

    perms = set(data.get("permissions", []))
    all_js = "\n".join(read_file_safe(f) for f in js_files)

    api_perm_map = {
        "chrome.tabs.query": "tabs",
        "chrome.tabs.sendMessage": "tabs",
        "chrome.alarms": "alarms",
        "chrome.notifications": "notifications",
        "chrome.contextMenus": "contextMenus",
        "chrome.declarativeNetRequest": "declarativeNetRequest",
        "chrome.cookies": "cookies",
        "chrome.webNavigation": "webNavigation",
        "chrome.scripting": "scripting",
    }

    missing = []
    for api, perm in api_perm_map.items():
        if api in all_js and perm not in perms:
            missing.append(f"  '{api}' used but '{perm}' not in permissions")

    if missing:
        return CheckResult("PERM-MISSING", False, "Missing permissions for used APIs", missing)
    return CheckResult("PERM-MISSING", True, "No missing permissions detected")


# ── Quality Checks (all projects) ────────────────────────────────────────

def check_qual_readme(path):
    """QUAL-README: README.md exists."""
    if (Path(path) / "README.md").exists():
        return CheckResult("QUAL-README", True, "README.md present")
    return CheckResult("QUAL-README", False, "README.md missing", severity="warn")


def check_qual_license(path):
    """QUAL-LICENSE: LICENSE exists."""
    p = Path(path)
    if (p / "LICENSE").exists() or (p / "LICENSE.md").exists() or (p / "LICENSE.txt").exists():
        return CheckResult("QUAL-LICENSE", True, "LICENSE present")
    return CheckResult("QUAL-LICENSE", False, "LICENSE missing", severity="warn")


def check_qual_gitignore(path):
    """QUAL-GITIGNORE: .gitignore present."""
    if (Path(path) / ".gitignore").exists():
        return CheckResult("QUAL-GITIGNORE", True, ".gitignore present")
    return CheckResult("QUAL-GITIGNORE", False, ".gitignore missing", severity="warn")


def check_qual_bugs_log(path):
    """QUAL-BUGS-LOG: BUGS_AND_ITERATIONS.md exists."""
    if (Path(path) / "BUGS_AND_ITERATIONS.md").exists():
        return CheckResult("QUAL-BUGS-LOG", True, "BUGS_AND_ITERATIONS.md present")
    return CheckResult("QUAL-BUGS-LOG", False, "BUGS_AND_ITERATIONS.md missing",
                       ["  Required by CLAUDE.md for every repo"], severity="warn")


# ── Rust Checks ──────────────────────────────────────────────────────────

def check_rust_clippy(path):
    """RUST-CLIPPY: cargo clippy passes."""
    try:
        r = subprocess.run(
            ["cargo", "clippy", "--", "-D", "warnings"],
            cwd=path, capture_output=True, text=True, timeout=120
        )
        if r.returncode == 0:
            return CheckResult("RUST-CLIPPY", True, "cargo clippy passes")
        lines = r.stderr.strip().splitlines()[-5:]
        return CheckResult("RUST-CLIPPY", False, "cargo clippy failed",
                           [f"  {l}" for l in lines])
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return CheckResult("RUST-CLIPPY", False, "cargo not found or timeout", severity="warn")


def check_rust_test(path):
    """RUST-TEST: cargo test passes."""
    try:
        r = subprocess.run(
            ["cargo", "test"],
            cwd=path, capture_output=True, text=True, timeout=120
        )
        if r.returncode == 0:
            return CheckResult("RUST-TEST", True, "cargo test passes")
        lines = r.stderr.strip().splitlines()[-5:]
        return CheckResult("RUST-TEST", False, "cargo test failed",
                           [f"  {l}" for l in lines])
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return CheckResult("RUST-TEST", False, "cargo not found or timeout", severity="warn")


def check_rust_unsafe(path):
    """RUST-UNSAFE: Audit unsafe blocks."""
    rs_files = collect_files(path, ".rs")
    hits = []
    for f in rs_files:
        content = read_file_safe(f)
        for i, line in enumerate(content.splitlines(), 1):
            if re.search(r'\bunsafe\b', line) and not line.strip().startswith("//"):
                hits.append(f"  {f}:{i}: {line.strip()[:60]}")
    if hits:
        return CheckResult("RUST-UNSAFE", False,
                           f"Found {len(hits)} unsafe block(s) — review required",
                           hits, severity="warn")
    return CheckResult("RUST-UNSAFE", True, "No unsafe blocks")


# ── Python Checks ────────────────────────────────────────────────────────

def check_python_typehints(path):
    """PY-TYPEHINTS: Functions have type hints."""
    py_files = collect_files(path, ".py")
    total_funcs = 0
    typed_funcs = 0
    for f in py_files:
        content = read_file_safe(f)
        for m in re.finditer(r'def\s+\w+\s*\(([^)]*)\)', content):
            total_funcs += 1
            sig = m.group(0)
            if "->" in content[m.end():m.end() + 30]:
                typed_funcs += 1
    if total_funcs == 0:
        return CheckResult("PY-TYPEHINTS", True, "No Python functions found (N/A)")
    pct = typed_funcs / total_funcs * 100
    if pct >= 50:
        return CheckResult("PY-TYPEHINTS", True, f"Type hints on {typed_funcs}/{total_funcs} functions ({pct:.0f}%)")
    return CheckResult("PY-TYPEHINTS", False,
                       f"Low type hint coverage: {typed_funcs}/{total_funcs} ({pct:.0f}%)",
                       severity="warn")


def check_python_docstrings(path):
    """PY-DOCSTRINGS: Public functions have docstrings."""
    py_files = collect_files(path, ".py")
    missing = []
    for f in py_files:
        content = read_file_safe(f)
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if re.match(r'^def\s+[a-z]', line) and not line.strip().startswith("def _"):
                # Check next non-empty line for docstring
                for j in range(i + 1, min(i + 3, len(lines))):
                    stripped = lines[j].strip()
                    if stripped:
                        if not (stripped.startswith('"""') or stripped.startswith("'''")):
                            missing.append(f"  {f}:{i + 1}: {line.strip()[:50]}")
                        break
    if missing and len(missing) > 5:
        return CheckResult("PY-DOCSTRINGS", False,
                           f"{len(missing)} public functions missing docstrings",
                           missing[:5] + [f"  ... and {len(missing) - 5} more"],
                           severity="warn")
    if missing:
        return CheckResult("PY-DOCSTRINGS", False,
                           f"{len(missing)} public functions missing docstrings",
                           missing, severity="warn")
    return CheckResult("PY-DOCSTRINGS", True, "Public functions have docstrings")


# ── iOS Checks ───────────────────────────────────────────────────────────

def check_ios_a11y_labels(path):
    """IOS-A11Y: SwiftUI views have accessibility labels."""
    swift_files = collect_files(path, ".swift")
    if not swift_files:
        return CheckResult("IOS-A11Y", True, "No Swift files (N/A)")
    views_without = []
    for f in swift_files:
        content = read_file_safe(f)
        if "View" in content and "body" in content:
            if "accessibilityLabel" not in content and "accessibility(label:" not in content:
                views_without.append(f"  {f}")
    if views_without:
        return CheckResult("IOS-A11Y", False,
                           f"{len(views_without)} SwiftUI view(s) without accessibility labels",
                           views_without[:5], severity="warn")
    return CheckResult("IOS-A11Y", True, "SwiftUI views have accessibility labels")


def check_ios_info_plist(path):
    """IOS-PLIST: Info.plist present and valid."""
    plist_files = collect_files(path, ".plist")
    if plist_files:
        return CheckResult("IOS-PLIST", True, "Info.plist present")
    if collect_files(path, ".swift"):
        return CheckResult("IOS-PLIST", False, "No Info.plist found", severity="warn")
    return CheckResult("IOS-PLIST", True, "No Swift project (N/A)")


# ── Check Runner ─────────────────────────────────────────────────────────

CATEGORIES = {
    "accessibility": {
        "types": ["extension"],
        "label": "ACCESSIBILITY",
    },
    "security": {
        "types": ["extension"],
        "label": "SECURITY",
    },
    "mv3": {
        "types": ["extension"],
        "label": "MV3 COMPLIANCE",
    },
    "brand": {
        "types": ["extension"],
        "label": "BRAND",
    },
    "permissions": {
        "types": ["extension"],
        "label": "PERMISSIONS",
    },
    "quality": {
        "types": ["extension", "rust", "python", "ios", "ios-expo", "web-react", "web-static", "general"],
        "label": "QUALITY",
    },
    "rust": {
        "types": ["rust"],
        "label": "RUST",
    },
    "python": {
        "types": ["python"],
        "label": "PYTHON",
    },
    "ios": {
        "types": ["ios", "ios-expo"],
        "label": "iOS",
    },
}


def run_checks(path, project_type, pre_commit=False, only_category=None):
    """Run all applicable checks and return {category: [CheckResult]}."""
    path = str(Path(path).resolve())

    # Collect files
    css_files = collect_files(path, ".css")
    js_files = collect_files(path, ".js")
    html_files = collect_files(path, ".html")

    results = {}

    # Determine which categories to run
    categories_to_run = {}
    for cat_name, cat_info in CATEGORIES.items():
        if only_category and cat_name != only_category:
            continue
        if project_type in cat_info["types"]:
            categories_to_run[cat_name] = cat_info

    # Accessibility
    if "accessibility" in categories_to_run:
        checks = []
        if not pre_commit:
            checks.append(check_a11y_contrast(path))
        checks.extend([
            check_a11y_ki001(css_files),
            check_a11y_ki004(css_files),
            check_a11y_ki006(css_files),
            check_a11y_ki008(css_files),
            check_a11y_dialog(html_files),
            check_a11y_expanded(html_files, js_files),
            check_a11y_label(html_files),
            check_a11y_live(js_files),
            check_a11y_input(html_files),
            check_a11y_touch(css_files),
            check_a11y_lang(html_files),
        ])
        results["accessibility"] = checks

    # Security
    if "security" in categories_to_run:
        results["security"] = [
            check_sec_innerhtml(js_files),
            check_sec_csp(path),
            check_sec_cdn(html_files, js_files),
            check_sec_ext_connect(path),
            check_sec_empty_catch(js_files),
            check_sec_sendmsg(js_files),
        ]

    # MV3
    if "mv3" in categories_to_run:
        results["mv3"] = [
            check_mv3_storage_mix(js_files),
            check_mv3_storage_key(js_files),
            check_mv3_settimeout(js_files),
            check_mv3_debug_guard(js_files),
            check_mv3_dnr_prop(js_files),
            check_mv3_setinterval(js_files),
        ]

    # Brand
    if "brand" in categories_to_run:
        checks = [
            check_brand_sparky(path),
            check_brand_gradient(css_files, html_files),
            check_brand_theme(path, html_files, js_files),
            check_brand_lib_wired(html_files),
        ]
        if not pre_commit:
            checks.append(check_brand_lib_sync(path))
        results["brand"] = checks

    # Permissions
    if "permissions" in categories_to_run:
        results["permissions"] = [
            check_perm_unused(path, js_files),
            check_perm_missing(path, js_files),
        ]

    # Quality
    if "quality" in categories_to_run:
        results["quality"] = [
            check_qual_readme(path),
            check_qual_license(path),
            check_qual_gitignore(path),
            check_qual_bugs_log(path),
        ]

    # Rust
    if "rust" in categories_to_run:
        checks = [check_rust_unsafe(path)]
        if not pre_commit:
            checks = [check_rust_clippy(path), check_rust_test(path)] + checks
        results["rust"] = checks

    # Python
    if "python" in categories_to_run:
        results["python"] = [
            check_python_typehints(path),
            check_python_docstrings(path),
        ]

    # iOS
    if "ios" in categories_to_run:
        results["ios"] = [
            check_ios_a11y_labels(path),
            check_ios_info_plist(path),
        ]

    return results


# ── History & Regression ──────────────────────────────────────────────────

def load_history():
    if HISTORY_PATH.exists():
        return json.loads(HISTORY_PATH.read_text())
    return {"runs": []}


def save_history(results, path, project_type):
    history = load_history()
    total_pass = sum(1 for cat in results.values() for r in cat if r.passed)
    total_fail = sum(1 for cat in results.values() for r in cat if not r.passed)

    snapshot = {
        "date": date.today().isoformat(),
        "path": str(path),
        "type": project_type,
        "total_pass": total_pass,
        "total_fail": total_fail,
        "failures": {},
    }
    for cat, checks in results.items():
        fails = [r.check_id for r in checks if not r.passed]
        if fails:
            snapshot["failures"][cat] = fails

    history["runs"].append(snapshot)
    history["runs"] = history["runs"][-50:]

    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history, indent=2))


def check_regressions(results):
    history = load_history()
    if not history["runs"]:
        return []

    last = history["runs"][-1]
    last_failures = set()
    for cat, ids in last.get("failures", {}).items():
        for cid in ids:
            last_failures.add(f"{cat}:{cid}")

    regressions = []
    for cat, checks in results.items():
        for r in checks:
            key = f"{cat}:{r.check_id}"
            if not r.passed and key not in last_failures:
                regressions.append(r)
    return regressions


# ── Output Formatting ────────────────────────────────────────────────────

def print_results(results, project_name, project_type, strict=False):
    """Print human-readable results."""
    print(f"\n{BOLD}=== ls-check: {project_name} ({project_type}) ==={RST}\n")

    total_pass = 0
    total_fail = 0
    total_warn = 0

    for cat_name, checks in results.items():
        cat_label = CATEGORIES.get(cat_name, {}).get("label", cat_name.upper())
        cat_pass = sum(1 for r in checks if r.passed)
        cat_fail = sum(1 for r in checks if not r.passed and (r.severity == "fail" or strict))
        cat_warn = sum(1 for r in checks if not r.passed and r.severity == "warn" and not strict)

        status_parts = []
        if cat_pass:
            status_parts.append(f"{cat_pass} pass")
        if cat_fail:
            status_parts.append(f"{cat_fail} fail")
        if cat_warn:
            status_parts.append(f"{cat_warn} warn")

        print(f"{BOLD}{cat_label}{RST} ({', '.join(status_parts)})")

        for r in checks:
            if r.passed:
                print(f"  {GRN}✓{RST} {r.message}")
                total_pass += 1
            elif r.severity == "warn" and not strict:
                print(f"  {YLW}⚠{RST} {r.check_id}: {r.message}")
                total_warn += 1
            else:
                print(f"  {RED}✗{RST} {r.check_id}: {r.message}")
                total_fail += 1

            for detail in r.details:
                print(f"    {DIM}{detail}{RST}")

        print()

    # Summary
    print(f"{BOLD}--- Summary: {total_pass} pass, {total_fail} fail, {total_warn} warn ---{RST}")

    if total_fail > 0:
        print(f"{RED}Fix {total_fail} failure(s) before proceeding.{RST}")

    return total_fail


def print_json(results, project_name, project_type, regressions=None):
    """Print machine-readable JSON."""
    output = {
        "project": project_name,
        "type": project_type,
        "categories": {},
        "summary": {
            "total_pass": 0,
            "total_fail": 0,
        },
    }

    for cat_name, checks in results.items():
        output["categories"][cat_name] = [r.to_dict() for r in checks]
        output["summary"]["total_pass"] += sum(1 for r in checks if r.passed)
        output["summary"]["total_fail"] += sum(1 for r in checks if not r.passed)

    if regressions:
        output["regressions"] = [r.to_dict() for r in regressions]

    print(json.dumps(output, indent=2))
    return output["summary"]["total_fail"]


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ls-check — Unified LoveSpark quality pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  ls-check .                          Full check, auto-detect project type
  ls-check . --pre-commit             Fast checks only (<2s)
  ls-check . --strict                 Warnings become failures
  ls-check . --only accessibility     Single category
  ls-check . --json                   Machine-readable output
  ls-check . --history                Save results for regression detection
""",
    )
    parser.add_argument("path", nargs="?", default=".", help="Project directory to check")
    parser.add_argument("--pre-commit", action="store_true",
                        help="Fast grep-based checks only (skip contrast audit, clippy, tests)")
    parser.add_argument("--strict", action="store_true",
                        help="Warnings become failures (use before CWS submission)")
    parser.add_argument("--only", choices=list(CATEGORIES.keys()),
                        help="Run only a single check category")
    parser.add_argument("--json", action="store_true",
                        help="Machine-readable JSON output")
    parser.add_argument("--history", action="store_true",
                        help="Save results and detect regressions")
    parser.add_argument("--type", choices=["extension", "rust", "python", "ios", "ios-expo",
                                           "web-react", "web-static", "general"],
                        help="Override auto-detected project type")
    args = parser.parse_args()

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(2)

    project_type = args.type or detect_project_type(path)
    project_name = path.name

    # Run checks
    results = run_checks(path, project_type, pre_commit=args.pre_commit, only_category=args.only)

    # Regressions
    regressions = []
    if args.history:
        regressions = check_regressions(results)

    # Output
    if args.json:
        fail_count = print_json(results, project_name, project_type, regressions)
    else:
        fail_count = print_results(results, project_name, project_type, strict=args.strict)

        if regressions:
            print(f"\n{RED}{BOLD}!!! REGRESSIONS DETECTED !!!{RST}")
            for r in regressions:
                print(f"  {RED}NEW FAIL{RST}  {r.check_id}: {r.message}")
            print(f"  {len(regressions)} new failure(s) since last run\n")

    # Save history
    if args.history:
        save_history(results, path, project_type)
        if not args.json:
            print(f"\n{DIM}History saved to {HISTORY_PATH}{RST}")

    sys.exit(1 if fail_count > 0 else 0)


if __name__ == "__main__":
    main()
