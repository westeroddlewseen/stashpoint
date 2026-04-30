"""Freshness scoring for stashes based on last-used recency."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from stashpoint.storage import load_stashes
from stashpoint.history import load_history


class StashNotFoundError(KeyError):
    pass


@dataclass
class FreshnessResult:
    name: str
    last_used: Optional[float]   # Unix timestamp, or None
    age_days: Optional[float]    # Days since last use, or None
    score: int                   # 0-100
    grade: str                   # A / B / C / D / F
    label: str                   # human-readable label


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 50:
        return "C"
    if score >= 25:
        return "D"
    return "F"


def _label(age_days: Optional[float]) -> str:
    if age_days is None:
        return "never used"
    if age_days < 1:
        return "used today"
    if age_days < 7:
        return "used this week"
    if age_days < 30:
        return "used this month"
    if age_days < 90:
        return "used this quarter"
    return "stale"


def compute_freshness(
    name: str,
    *,
    _load_stashes=None,
    _load_history=None,
) -> FreshnessResult:
    """Compute freshness for a single stash."""
    _load_stashes = _load_stashes or load_stashes
    _load_history = _load_history or load_history

    stashes = _load_stashes()
    if name not in stashes:
        raise StashNotFoundError(name)

    history = _load_history()
    events = [e for e in history if e.get("stash") == name]

    if not events:
        return FreshnessResult(
            name=name,
            last_used=None,
            age_days=None,
            score=0,
            grade="F",
            label="never used",
        )

    last_ts = max(e["timestamp"] for e in events)
    now = time.time()
    age_days = (now - last_ts) / 86400.0

    # Score decays: 100 at 0 days, 0 at 180 days
    score = max(0, int(100 - (age_days / 180.0) * 100))
    grade = _grade(score)
    label = _label(age_days)

    return FreshnessResult(
        name=name,
        last_used=last_ts,
        age_days=round(age_days, 2),
        score=score,
        grade=grade,
        label=label,
    )
