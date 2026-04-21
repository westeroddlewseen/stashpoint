"""Lint stashes for common issues and best practices."""

from typing import Dict, List, NamedTuple


class LintIssue(NamedTuple):
    level: str  # 'warning' or 'error'
    key: str
    message: str


SUSPECT_KEY_PATTERNS = [
    ("PASSWORD", "warning", "Value may contain a plaintext password"),
    ("SECRET", "warning", "Value may contain a secret"),
    ("TOKEN", "warning", "Value may contain an access token"),
    ("API_KEY", "warning", "Value may contain an API key"),
    ("PRIVATE_KEY", "warning", "Value may contain a private key"),
]

MAX_VALUE_LENGTH = 1024
MAX_KEY_LENGTH = 128


def lint_stash(variables: Dict[str, str]) -> List[LintIssue]:
    """Analyse a stash's variables and return a list of lint issues."""
    issues: List[LintIssue] = []

    if not variables:
        issues.append(LintIssue("warning", "", "Stash is empty"))
        return issues

    for key, value in variables.items():
        # Key length
        if len(key) > MAX_KEY_LENGTH:
            issues.append(LintIssue("error", key, f"Key exceeds {MAX_KEY_LENGTH} characters"))

        # Value length
        if len(value) > MAX_VALUE_LENGTH:
            issues.append(LintIssue("warning", key, f"Value exceeds {MAX_VALUE_LENGTH} characters"))

        # Empty value
        if value == "":
            issues.append(LintIssue("warning", key, "Value is empty"))

        # Suspect sensitive key names
        upper_key = key.upper()
        for pattern, level, message in SUSPECT_KEY_PATTERNS:
            if pattern in upper_key:
                issues.append(LintIssue(level, key, message))
                break

        # Whitespace padding
        if value != value.strip():
            issues.append(LintIssue("warning", key, "Value has leading or trailing whitespace"))

    return issues


def format_lint(stash_name: str, issues: List[LintIssue]) -> str:
    """Format lint issues for display."""
    if not issues:
        return f"✓ {stash_name}: no issues found"

    lines = [f"Lint results for '{stash_name}':"]
    for issue in issues:
        prefix = "[ERROR]" if issue.level == "error" else "[WARN] "
        key_part = f" ({issue.key})" if issue.key else ""
        lines.append(f"  {prefix}{key_part} {issue.message}")
    return "\n".join(lines)
