"""Project file collection helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

IGNORED_DIRS = {
    ".git", "node_modules", "__pycache__", ".build", "build", "dist",
    ".venv", "venv", ".next", ".turbo", "coverage", ".pytest_cache",
}


@dataclass
class ProjectFiles:
    root: Path
    all_files: list[Path] = field(default_factory=list)
    by_ext: dict[str, list[Path]] = field(default_factory=dict)


def collect_project_files(path: str | Path) -> ProjectFiles:
    """Walk a project once and index files by extension."""
    root = Path(path)
    index = ProjectFiles(root=root)
    for current, dirs, files in __import__('os').walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for name in files:
            file_path = Path(current) / name
            index.all_files.append(file_path)
            index.by_ext.setdefault(file_path.suffix, []).append(file_path)
    return index
