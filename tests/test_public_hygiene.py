"""Public-repo hygiene guards.

This repo is public. Anything that identifies the author's machine (absolute
``/Users/<name>/...`` paths) must not land in the ledger — use repo-relative
or ``~/``-relative paths instead. See BUGS_AND_ITERATIONS.md BUG-001.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME_PATH_RE = re.compile(r"/Users/[A-Za-z0-9_.-]+/")


def test_ledger_has_no_machine_specific_home_paths():
    # BUG-001 regression: ledger/AGENT-AUDIT-LEDGER.md leaked an absolute
    # /Users/<name>/Projects/... path into the public record.
    hits = []
    for f in sorted((ROOT / "ledger").glob("*.md")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if HOME_PATH_RE.search(line):
                hits.append(f"{f.relative_to(ROOT)}:{i}: {line.strip()[:100]}")
    assert not hits, "machine-specific home paths in public ledger:\n" + "\n".join(hits)
