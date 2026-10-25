"""Project type detection for ls-check."""
from __future__ import annotations

import json
from pathlib import Path


def detect_project_type(path: str | Path) -> str:
    """Infer the LoveSpark project type from marker files."""
    p = Path(path)
    manifest = p / "manifest.json"
    if manifest.exists():
        try:
            if "manifest_version" in json.loads(manifest.read_text()):
                return "extension"
        except (json.JSONDecodeError, OSError):
            pass
    if (p / "Cargo.toml").exists():
        return "rust"
    if (p / "Package.swift").exists() or list(p.glob("*.xcodeproj")):
        return "ios"
    package_json = p / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "expo" in deps or "react-native" in deps:
                return "ios-expo"
            if "next" in deps or "react" in deps:
                return "web-react"
        except (json.JSONDecodeError, OSError):
            pass
    if (p / "pyproject.toml").exists() or (p / "setup.py").exists() or (p / "requirements.txt").exists():
        return "python"
    if (p / "index.html").exists():
        return "web-static"
    return "general"
