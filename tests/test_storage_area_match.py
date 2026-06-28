"""Regression tests for MV3-STORAGE-AREA-MATCH (KI-039).

A chrome.storage.onChanged listener that guards on an areaName the extension never
writes to is dead code — live updates silently require a page refresh. The check
flags a clear single-area mismatch (all writes to one area, guard on another) and
stays quiet on ambiguous / dual-area extensions.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WRITER = '(() => { chrome.storage.local.set({ pack: "retro-pink" }); })();\n'
LISTENER = (
    "(() => {\n"
    "  chrome.storage.onChanged.addListener((changes, areaName) => {\n"
    '    if (areaName !== "%s") {\n'
    "      return;\n"
    "    }\n"
    '    chrome.storage.local.get(["pack"], (next) => { void next; });\n'
    "  });\n"
    "})();\n"
)


def run_cmd(*args):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True)


def _area_match_result(tmp_path, guard_area, extra_writer=""):
    (tmp_path / "manifest.json").write_text(
        '{"manifest_version":3,"name":"x","version":"1.0"}'
    )
    (tmp_path / "popup.js").write_text(WRITER + extra_writer)
    (tmp_path / "content_script.js").write_text(LISTENER % guard_area)
    result = run_cmd(
        sys.executable, "scripts/ls-check.py", str(tmp_path),
        "--type", "extension", "--only", "mv3", "--json",
    )
    data = json.loads(result.stdout)
    checks = {c["id"]: c for c in data["categories"]["mv3"]}
    assert "MV3-STORAGE-AREA-MATCH" in checks, checks.keys()
    return checks["MV3-STORAGE-AREA-MATCH"]


def test_builtin_selftest_passes():
    result = run_cmd(sys.executable, "scripts/ls-check.py", "--selftest")
    assert result.returncode == 0, result.stdout + result.stderr


def test_prefix_guard_sync_writes_local_fails(tmp_path):
    # The exact LoveSpark-Retro-Cursor pre-fix shape: guard "sync", writes "local".
    res = _area_match_result(tmp_path, "sync")
    assert res["passed"] is False
    assert "storage.local" in res["message"]


def test_fixed_guard_local_writes_local_passes(tmp_path):
    res = _area_match_result(tmp_path, "local")
    assert res["passed"] is True


def test_dual_area_writer_not_flagged(tmp_path):
    # Writes to BOTH local and sync → ambiguous → conservatively passes.
    res = _area_match_result(
        tmp_path, "sync", extra_writer='(() => { chrome.storage.sync.set({ b: 2 }); })();\n'
    )
    assert res["passed"] is True
