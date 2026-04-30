"""Compute usage velocity (rate of use over time) for stashes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from stashpoint.storage import load_stashes
from stashpoint.history import load_history


class StashNotFoundError(KeyError):
    pass


@dataclass
class VelocityResult:
    name: str
    total_events: int
    events_last_7d: int
    events_last_30d: int
    daily_average_30d: float
    trend: str  # "rising", "steady", "falling", "inactive"


def _count_events_since(events: List[dict], since: datetime) -> int:
    count = 0
    for e in events:
        ts = e.get("timestamp")
        if ts is None:
            continue
        try:
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt >= since:
                count += 1
        except ValueError:
            continue
    return count


def _trend(last_7d: int, daily_avg_30d: float) -> str:
    weekly_avg = daily_avg_30d * 7
    if weekly_avg == 0 and last_7d == 0:
        return "inactive"
    if weekly_avg == 0:
        return "rising"
    ratio = last_7d / weekly_avg
    if ratio >= 1.25:
        return "rising"
    if ratio <= 0.75:
        return "falling"
    return "steady"


def compute_velocity(name: str) -> VelocityResult:
    """Compute velocity metrics for a named stash."""
    stashes = load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    history = load_history()
    events = [e for e in history if e.get("stash") == name]

    now = datetime.now(tz=timezone.utc)
    since_7d = now - timedelta(days=7)
    since_30d = now - timedelta(days=30)

    last_7d = _count_events_since(events, since_7d)
    last_30d = _count_events_since(events, since_30d)
    daily_avg = round(last_30d / 30.0, 2)
    trend = _trend(last_7d, daily_avg)

    return VelocityResult(
        name=name,
        total_events=len(events),
        events_last_7d=last_7d,
        events_last_30d=last_30d,
        daily_average_30d=daily_avg,
        trend=trend,
    )
