"""Tests for stashpoint.badge."""

import time
import pytest
from unittest.mock import patch
from stashpoint.badge import (
    compute_badges,
    format_badges,
    BadgeResult,
    StashNotFoundError,
)


STASHES = {
    "myapp": {f"VAR_{i}": str(i) for i in range(5)},
    "tiny": {"A": "1"},
    "huge": {f"K{i}": str(i) for i in range(25)},
    "empty-ish": {"X": "1", "Y": "2"},
}

FAVORITES = {"myapp"}
RATINGS = {"myapp": 5}


@pytest.fixture()
def mock_deps():
    now = time.time()
    history = (
        [{"stash": "myapp", "event": "save", "timestamp": now - 3600} for _ in range(12)]
        + [{"stash": "myapp", "event": "load", "timestamp": now - 100} for _ in range(6)]
    )
    with (
        patch("stashpoint.badge.load_stashes", return_value=STASHES),
        patch("stashpoint.badge.load_history", return_value=history),
        patch("stashpoint.badge.load_favorites", return_value=FAVORITES),
        patch("stashpoint.badge.load_ratings", return_value=RATINGS),
    ):
        yield


def test_stash_not_found_raises(mock_deps):
    with pytest.raises(StashNotFoundError):
        compute_badges("nonexistent")


def test_starred_badge_awarded_to_favorite(mock_deps):
    result = compute_badges("myapp")
    assert "starred" in result.badges


def test_starred_badge_not_awarded_to_non_favorite(mock_deps):
    result = compute_badges("tiny")
    assert "starred" not in result.badges


def test_veteran_badge_for_high_event_count(mock_deps):
    result = compute_badges("myapp")
    assert "veteran" in result.badges


def test_veteran_badge_absent_for_low_event_count(mock_deps):
    result = compute_badges("tiny")
    assert "veteran" not in result.badges


def test_rich_badge_for_large_stash(mock_deps):
    result = compute_badges("huge")
    assert "rich" in result.badges


def test_minimalist_badge_for_small_stash(mock_deps):
    result = compute_badges("tiny")
    assert "minimalist" in result.badges


def test_minimalist_and_rich_are_mutually_exclusive(mock_deps):
    rich_result = compute_badges("huge")
    tiny_result = compute_badges("tiny")
    assert "minimalist" not in rich_result.badges
    assert "rich" not in tiny_result.badges


def test_top_rated_badge_for_rating_5(mock_deps):
    result = compute_badges("myapp")
    assert "top-rated" in result.badges


def test_top_rated_badge_absent_without_rating(mock_deps):
    result = compute_badges("tiny")
    assert "top-rated" not in result.badges


def test_active_badge_for_recent_events(mock_deps):
    result = compute_badges("myapp")
    assert "active" in result.badges


def test_format_badges_no_badges():
    result = BadgeResult(stash_name="plain", badges=[])
    output = format_badges(result)
    assert "No badges" in output
    assert "plain" in output


def test_format_badges_lists_earned_badges(mock_deps):
    result = compute_badges("myapp")
    output = format_badges(result)
    assert "myapp" in output
    assert "starred" in output.lower() or "⭐" in output
