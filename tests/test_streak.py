"""Tests for stashpoint.streak."""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

import pytest

from stashpoint.streak import (
    StreakResult,
    StashNotFoundError,
    compute_streak,
)


STASHES = {"myapp": {"FOO": "bar"}, "other": {}}


def _make_history(*offsets: int, stash: str = "myapp") -> list[dict]:
    """Build history entries for `stash` at today minus each offset (days)."""
    today = date.today()
    return [
        {"stash": stash, "timestamp": (today - timedelta(days=d)).isoformat()}
        for d in offsets
    ]


@pytest.fixture(autouse=True)
def mock_load_stashes():
    with patch("stashpoint.streak.load_stashes", return_value=STASHES):
        yield


def test_stash_not_found_raises():
    with pytest.raises(StashNotFoundError):
        compute_streak("nonexistent")


def test_no_history_returns_zero_streak():
    with patch("stashpoint.streak.load_history", return_value=[]):
        result = compute_streak("myapp")
    assert result.current_streak == 0
    assert result.longest_streak == 0
    assert result.last_used is None


def test_single_use_today():
    history = _make_history(0)
    with patch("stashpoint.streak.load_history", return_value=history):
        result = compute_streak("myapp")
    assert result.current_streak == 1
    assert result.last_used == date.today().isoformat()


def test_consecutive_days_streak():
    # Used today, yesterday, two days ago → streak of 3
    history = _make_history(0, 1, 2)
    with patch("stashpoint.streak.load_history", return_value=history):
        result = compute_streak("myapp")
    assert result.current_streak == 3
    assert result.longest_streak == 3


def test_broken_streak_resets_current():
    # Last used 5 days ago — streak should be 0
    history = _make_history(5, 6, 7)
    with patch("stashpoint.streak.load_history", return_value=history):
        result = compute_streak("myapp")
    assert result.current_streak == 0
    assert result.longest_streak == 3


def test_longest_streak_recorded():
    # A run of 4 days ending 10 days ago, then a single use today
    history = _make_history(0, 10, 11, 12, 13)
    with patch("stashpoint.streak.load_history", return_value=history):
        result = compute_streak("myapp")
    assert result.longest_streak == 4
    assert result.current_streak == 1


def test_ignores_other_stash_history():
    history = _make_history(0, 1, 2, stash="other") + _make_history(5, stash="myapp")
    with patch("stashpoint.streak.load_history", return_value=history):
        result = compute_streak("myapp")
    # Only the single entry 5 days ago counts for myapp
    assert result.current_streak == 0


def test_result_is_dataclass():
    history = _make_history(0)
    with patch("stashpoint.streak.load_history", return_value=history):
        result = compute_streak("myapp")
    assert isinstance(result, StreakResult)
    assert result.name == "myapp"
