"""Public-repo hygiene guards.

This repo is public. Anything that identifies the author's machine (absolute
macOS home-directory paths) or the author's personal/health state must not
land in tracked files. Use repo-relative or ``~/``-relative paths and
generalized wording ("an exhausted user"). See BUGS_AND_ITERATIONS.md
BUG-001 and BUG-003.

The patterns use bracket classes (``Use[r]s``, ``9[0]h``) so this file does not
contain the literal strings it guards against.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME_PATH_RE = re.compile(r"/Use[r]s/[A-Za-z0-9_.-]+/")
HEALTH_RE = re.compile(r"9[0]h|fast[i]ng|24h-awak[e]", re.IGNORECASE)


def _tracked_text_files():
    try:
        out = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.split()
        files = [ROOT / f for f in out]
    except (OSError, subprocess.CalledProcessError):
        files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
    for f in files:
        try:
            yield f, f.read_text()
        except (UnicodeDecodeError, OSError):
            continue


def test_ledger_has_no_machine_specific_home_paths():
    # BUG-001 regression: ledger/AGENT-AUDIT-LEDGER.md leaked an absolute
    # home-directory path into the public record.
    hits = []
    for f in sorted((ROOT / "ledger").glob("*.md")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if HOME_PATH_RE.search(line):
                hits.append(f"{f.relative_to(ROOT)}:{i}: {line.strip()[:100]}")
    assert not hits, "machine-specific home paths in public ledger:\n" + "\n".join(hits)


def test_tracked_files_have_no_raw_health_wording():
    # BUG-003 regression: BUGS_AND_ITERATIONS.md quoted the scrubbed raw
    # health wording verbatim; the ledger-only check missed it.
    hits = []
    for f, text in _tracked_text_files():
        for i, line in enumerate(text.splitlines(), 1):
            if HEALTH_RE.search(line):
                hits.append(f"{f.relative_to(ROOT)}:{i}")
    assert not hits, "raw personal health wording in public repo:\n" + "\n".join(hits)
