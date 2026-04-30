"""Tests for stashpoint.velocity."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from stashpoint.velocity import (
    VelocityResult,
    StashNotFoundError,
    compute_velocity,
    _trend,
)


def _ts(days_ago: float) -> str:
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


@pytest.fixture()
def mock_deps(monkeypatch):
    stashes = {"myapp": {"FOO": "bar"}}
    history = [
        {"stash": "myapp", "event": "load", "timestamp": _ts(1)},
        {"stash": "myapp", "event": "load", "timestamp": _ts(3)},
        {"stash": "myapp", "event": "save", "timestamp": _ts(10)},
        {"stash": "myapp", "event": "load", "timestamp": _ts(20)},
        {"stash": "other", "event": "load", "timestamp": _ts(1)},
    ]
    monkeypatch.setattr("stashpoint.velocity.load_stashes", lambda: stashes)
    monkeypatch.setattr("stashpoint.velocity.load_history", lambda: history)
    return stashes, history


def test_stash_not_found_raises(monkeypatch):
    monkeypatch.setattr("stashpoint.velocity.load_stashes", lambda: {})
    monkeypatch.setattr("stashpoint.velocity.load_history", lambda: [])
    with pytest.raises(StashNotFoundError):
        compute_velocity("ghost")


def test_result_is_dataclass(mock_deps):
    result = compute_velocity("myapp")
    assert isinstance(result, VelocityResult)


def test_result_name(mock_deps):
    result = compute_velocity("myapp")
    assert result.name == "myapp"


def test_total_events_counts_only_target_stash(mock_deps):
    result = compute_velocity("myapp")
    assert result.total_events == 4


def test_events_last_7d(mock_deps):
    result = compute_velocity("myapp")
    # days_ago 1, 3 are within 7 days; 10 and 20 are not
    assert result.events_last_7d == 2


def test_events_last_30d(mock_deps):
    result = compute_velocity("myapp")
    # days_ago 1, 3, 10, 20 all within 30 days
    assert result.events_last_30d == 4


def test_daily_average_30d(mock_deps):
    result = compute_velocity("myapp")
    assert result.daily_average_30d == round(4 / 30.0, 2)


def test_trend_inactive():
    assert _trend(0, 0.0) == "inactive"


def test_trend_rising_from_zero():
    assert _trend(5, 0.0) == "rising"


def test_trend_rising():
    # last_7d much higher than weekly average
    assert _trend(10, 1.0) == "rising"  # weekly_avg=7, ratio=10/7 > 1.25


def test_trend_falling():
    assert _trend(1, 2.0) == "falling"  # weekly_avg=14, ratio=1/14 < 0.75


def test_trend_steady():
    assert _trend(7, 1.0) == "steady"  # ratio == 1.0


def test_no_history_returns_inactive(monkeypatch):
    monkeypatch.setattr("stashpoint.velocity.load_stashes", lambda: {"empty": {}})
    monkeypatch.setattr("stashpoint.velocity.load_history", lambda: [])
    result = compute_velocity("empty")
    assert result.trend == "inactive"
    assert result.total_events == 0
