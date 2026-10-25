"""Structured result models for agent/CI-facing reports."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import __version__

SCHEMA_VERSION = "1.0"


@dataclass
class CheckResult:
    id: str
    passed: bool
    message: str
    details: list[str] = field(default_factory=list)
    severity: str = "fail"
    category: str = "general"
    rule_source: str | None = None
    wcag: list[str] = field(default_factory=list)
    suggestion: str | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "severity": self.severity,
            "category": self.category,
            "rule_source": self.rule_source,
            "wcag": self.wcag,
            "suggestion": self.suggestion,
            "evidence": self.evidence,
        }


def build_report(tool: str, project: str, project_type: str, categories: dict[str, list[CheckResult]]) -> dict[str, Any]:
    """Build a schema-versioned report from grouped check results."""
    output: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "tool": tool,
        "tool_version": __version__,
        "project": project,
        "type": project_type,
        "categories": {},
        "summary": {"total_pass": 0, "total_fail": 0, "total_warn": 0},
    }
    for category, checks in categories.items():
        output["categories"][category] = [check.to_dict() for check in checks]
        output["summary"]["total_pass"] += sum(1 for check in checks if check.passed)
        output["summary"]["total_fail"] += sum(1 for check in checks if not check.passed and check.severity == "fail")
        output["summary"]["total_warn"] += sum(1 for check in checks if not check.passed and check.severity == "warn")
    return output
