"""Sentiment scoring for stash variable names and values.

Provides a lightweight heuristic analysis of a stash's contents,
flagging variables that look like secrets, deprecated patterns,
or overly terse names.
"""

from dataclasses import dataclass, field
from typing import List

from stashpoint.storage import load_stash, load_stashes

SECRET_KEYWORDS = {"password", "secret", "token", "key", "passwd", "apikey", "api_key", "auth"}
DEPRECATED_PREFIXES = ("OLD_", "DEPRECATED_", "LEGACY_", "TMP_", "TEMP_")
TERSE_MAX_LEN = 2


class StashNotFoundError(KeyError):
    pass


@dataclass
class SentimentIssue:
    variable: str
    kind: str  # 'secret', 'deprecated', 'terse', 'empty_value'
    message: str


@dataclass
class SentimentResult:
    stash_name: str
    issues: List[SentimentIssue] = field(default_factory=list)

    @property
    def score(self) -> int:
        """Lower is worse. Starts at 100, deducted per issue."""
        deductions = {"secret": 20, "deprecated": 10, "terse": 5, "empty_value": 15}
        total = 100
        for issue in self.issues:
            total -= deductions.get(issue.kind, 5)
        return max(0, total)


def analyse_stash(name: str) -> SentimentResult:
    """Analyse a single stash and return a SentimentResult."""
    stashes = load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    variables = stashes[name]
    result = SentimentResult(stash_name=name)

    for var, value in variables.items():
        lower = var.lower()

        if any(kw in lower for kw in SECRET_KEYWORDS):
            result.issues.append(SentimentIssue(
                variable=var,
                kind="secret",
                message=f"'{var}' looks like a sensitive credential.",
            ))

        if any(var.startswith(prefix) for prefix in DEPRECATED_PREFIXES):
            result.issues.append(SentimentIssue(
                variable=var,
                kind="deprecated",
                message=f"'{var}' uses a deprecated naming prefix.",
            ))

        if len(var) <= TERSE_MAX_LEN:
            result.issues.append(SentimentIssue(
                variable=var,
                kind="terse",
                message=f"'{var}' is very short and may be unclear.",
            ))

        if value == "":
            result.issues.append(SentimentIssue(
                variable=var,
                kind="empty_value",
                message=f"'{var}' has an empty value.",
            ))

    return result


def format_sentiment(result: SentimentResult) -> str:
    lines = [f"Sentiment analysis for '{result.stash_name}' — score: {result.score}/100"]
    if not result.issues:
        lines.append("  No issues found.")
    else:
        for issue in result.issues:
            lines.append(f"  [{issue.kind.upper()}] {issue.message}")
    return "\n".join(lines)
