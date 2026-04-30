"""Tests for stashpoint.freshness."""

import time
import pytest

from stashpoint.freshness import (
    FreshnessResult,
    StashNotFoundError,
    compute_freshness,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_STASHES = {"myapp": {"FOO": "bar"}, "other": {}}


def _mock(events):
    """Return keyword-argument overrides for compute_freshness."""
    return {
        "_load_stashes": lambda: _STASHES,
        "_load_history": lambda: events,
    }


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


def test_stash_not_found_raises():
    with pytest.raises(StashNotFoundError):
        compute_freshness(
            "missing",
            **_mock([]),
        )


def test_never_used_score_is_zero():
    result = compute_freshness("myapp", **_mock([]))
    assert result.score == 0


def test_never_used_grade_is_f():
    result = compute_freshness("myapp", **_mock([]))
    assert result.grade == "F"


def test_never_used_label():
    result = compute_freshness("myapp", **_mock([]))
    assert result.label == "never used"


def test_never_used_last_used_is_none():
    result = compute_freshness("myapp", **_mock([]))
    assert result.last_used is None
    assert result.age_days is None


def test_used_today_high_score():
    events = [{"stash": "myapp", "timestamp": time.time() - 60}]
    result = compute_freshness("myapp", **_mock(events))
    assert result.score >= 99
    assert result.grade == "A"


def test_used_today_label():
    events = [{"stash": "myapp", "timestamp": time.time() - 3600}]
    result = compute_freshness("myapp", **_mock(events))
    assert result.label == "used today"


def test_used_this_week_label():
    events = [{"stash": "myapp", "timestamp": time.time() - 86400 * 3}]
    result = compute_freshness("myapp", **_mock(events))
    assert result.label == "used this week"


def test_stale_label_for_old_stash():
    events = [{"stash": "myapp", "timestamp": time.time() - 86400 * 200}]
    result = compute_freshness("myapp", **_mock(events))
    assert result.label == "stale"
    assert result.score == 0
    assert result.grade == "F"


def test_most_recent_event_is_used():
    now = time.time()
    events = [
        {"stash": "myapp", "timestamp": now - 86400 * 100},
        {"stash": "myapp", "timestamp": now - 60},   # most recent
    ]
    result = compute_freshness("myapp", **_mock(events))
    assert result.score >= 99


def test_result_is_dataclass():
    events = [{"stash": "myapp", "timestamp": time.time()}]
    result = compute_freshness("myapp", **_mock(events))
    assert isinstance(result, FreshnessResult)
    assert result.name == "myapp"


def test_unrelated_events_ignored():
    events = [{"stash": "other", "timestamp": time.time()}]
    result = compute_freshness("myapp", **_mock(events))
    assert result.score == 0
    assert result.last_used is None
