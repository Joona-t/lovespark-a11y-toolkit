"""Per-project history paths."""
from __future__ import annotations

from pathlib import Path


def default_history_path(project_path: str | Path, name: str = "ls-check-history.json") -> Path:
    """Return the project-local history file path."""
    return Path(project_path).resolve() / ".lovespark" / name
