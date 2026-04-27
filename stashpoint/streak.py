"""Track usage streaks for stashes."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from stashpoint.storage import load_stashes
from stashpoint.history import load_history


class StashNotFoundError(Exception):
    pass


@dataclass
class StreakResult:
    name: str
    current_streak: int
    longest_streak: int
    last_used: Optional[str]  # ISO date string or None


def get_streak_path() -> Path:
    base = Path(os.environ.get("STASHPOINT_DIR", Path.home() / ".stashpoint"))
    return base / "streaks.json"


def load_streaks() -> dict:
    path = get_streak_path()
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_streaks(streaks: dict) -> None:
    path = get_streak_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(streaks, f, indent=2)


def _extract_use_dates(name: str) -> list[date]:
    """Return sorted unique dates on which a stash was used."""
    history = load_history()
    dates = set()
    for entry in history:
        if entry.get("stash") == name:
            ts = entry.get("timestamp", "")
            if ts:
                try:
                    dates.add(date.fromisoformat(ts[:10]))
                except ValueError:
                    pass
    return sorted(dates)


def compute_streak(name: str) -> StreakResult:
    stashes = load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    use_dates = _extract_use_dates(name)

    if not use_dates:
        return StreakResult(name=name, current_streak=0, longest_streak=0, last_used=None)

    last_used = use_dates[-1].isoformat()
    today = date.today()

    # Compute longest and current streaks
    longest = 1
    current_run = 1
    for i in range(1, len(use_dates)):
        if use_dates[i] - use_dates[i - 1] == timedelta(days=1):
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    # Current streak: consecutive days ending today or yesterday
    current_streak = 1
    for i in range(len(use_dates) - 1, 0, -1):
        if use_dates[i] - use_dates[i - 1] == timedelta(days=1):
            current_streak += 1
        else:
            break

    # Reset current streak if last use wasn't today or yesterday
    if today - use_dates[-1] > timedelta(days=1):
        current_streak = 0

    return StreakResult(
        name=name,
        current_streak=current_streak,
        longest_streak=max(longest, current_streak),
        last_used=last_used,
    )
