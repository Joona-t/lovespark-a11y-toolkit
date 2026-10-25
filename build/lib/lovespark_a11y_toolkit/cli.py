"""Console entrypoints for legacy-compatible LoveSpark CLIs."""
from __future__ import annotations

import runpy
from pathlib import Path


def _run_script(name: str) -> None:
    """Run a legacy script as the current process entrypoint."""
    script = Path(__file__).resolve().parents[1] / "scripts" / name
    runpy.run_path(str(script), run_name="__main__")


def ls_check_main() -> None:
    """Console entrypoint for ls-check."""
    _run_script("ls-check.py")


def audit_contrast_main() -> None:
    """Console entrypoint for ls-audit-contrast."""
    _run_script("audit-contrast.py")
