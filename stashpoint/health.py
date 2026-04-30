"""Health check module for stashpoint stashes."""

from dataclasses import dataclass, field
from typing import List, Optional

from stashpoint.storage import load_stashes, load_stash
from stashpoint.lock import is_locked
from stashpoint.expire import load_expiry
from stashpoint.validate import validate_stash, ValidationError

import time


class StashNotFoundError(Exception):
    pass


@dataclass
class HealthIssue:
    severity: str  # "error", "warning", "info"
    message: str


@dataclass
class HealthReport:
    name: str
    healthy: bool
    issues: List[HealthIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[HealthIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[HealthIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def check_stash_health(name: str) -> HealthReport:
    """Run health checks on a named stash and return a HealthReport."""
    stashes = load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    variables = stashes[name]
    issues: List[HealthIssue] = []

    # Check for empty stash
    if not variables:
        issues.append(HealthIssue(severity="warning", message="Stash has no variables."))

    # Validate variable names and values
    try:
        validate_stash(variables)
    except ValidationError as e:
        issues.append(HealthIssue(severity="error", message=str(e)))

    # Check for expiry
    expiry_store = load_expiry()
    if name in expiry_store:
        expires_at = expiry_store[name]
        now = time.time()
        if expires_at < now:
            issues.append(HealthIssue(severity="error", message="Stash has expired."))
        elif expires_at - now < 86400:
            issues.append(HealthIssue(severity="warning", message="Stash expires within 24 hours."))

    # Check for empty values
    for key, value in variables.items():
        if value == "":
            issues.append(HealthIssue(severity="warning", message=f"Variable '{key}' has an empty value."))

    healthy = not any(i.severity == "error" for i in issues)
    return HealthReport(name=name, healthy=healthy, issues=issues)


def check_all_health() -> List[HealthReport]:
    """Run health checks on all stashes."""
    stashes = load_stashes()
    return [check_stash_health(name) for name in sorted(stashes)]


def format_health_report(report: HealthReport) -> str:
    """Format a HealthReport as a human-readable string."""
    status = "OK" if report.healthy else "UNHEALTHY"
    lines = [f"[{status}] {report.name}"]
    for issue in report.issues:
        prefix = {"error": "  ERROR", "warning": "  WARN ", "info": "  INFO "}.get(issue.severity, "  ?    ")
        lines.append(f"{prefix}: {issue.message}")
    return "\n".join(lines)
