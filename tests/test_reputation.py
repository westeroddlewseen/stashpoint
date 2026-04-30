"""Tests for stashpoint.reputation."""

import pytest
from unittest.mock import patch

from stashpoint.reputation import compute_reputation, StashNotFoundError, _grade


@pytest.fixture
def mock_deps(monkeypatch):
    stashes = {"myapp": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"}}
    history = [
        {"stash": "myapp", "action": "load"},
        {"stash": "myapp", "action": "load"},
        {"stash": "other", "action": "load"},
    ]
    favorites = ["myapp"]
    ratings = {"myapp": 4}
    tags = {"myapp": ["production", "db"]}

    return {
        "_load_stashes": lambda: stashes,
        "_load_history": lambda: history,
        "_load_favorites": lambda: favorites,
        "_load_ratings": lambda: ratings,
        "_load_tags": lambda: tags,
    }


def test_stash_not_found_raises():
    result_fn = compute_reputation
    with pytest.raises(StashNotFoundError):
        compute_reputation(
            "nonexistent",
            _load_stashes=lambda: {},
            _load_history=lambda: [],
            _load_favorites=lambda: [],
            _load_ratings=lambda: {},
            _load_tags=lambda: {},
        )


def test_result_name(mock_deps):
    result = compute_reputation("myapp", **mock_deps)
    assert result.name == "myapp"


def test_result_has_score(mock_deps):
    result = compute_reputation("myapp", **mock_deps)
    assert 0.0 <= result.score <= 100.0


def test_result_has_grade(mock_deps):
    result = compute_reputation("myapp", **mock_deps)
    assert result.grade in ("A", "B", "C", "D", "F")


def test_signals_list_not_empty(mock_deps):
    result = compute_reputation("myapp", **mock_deps)
    assert len(result.signals) > 0


def test_favorite_adds_to_score():
    base = compute_reputation(
        "s",
        _load_stashes=lambda: {"s": {"K": "V"}},
        _load_history=lambda: [],
        _load_favorites=lambda: [],
        _load_ratings=lambda: {},
        _load_tags=lambda: {},
    )
    with_fav = compute_reputation(
        "s",
        _load_stashes=lambda: {"s": {"K": "V"}},
        _load_history=lambda: [],
        _load_favorites=lambda: ["s"],
        _load_ratings=lambda: {},
        _load_tags=lambda: {},
    )
    assert with_fav.score > base.score


def test_score_capped_at_100():
    result = compute_reputation(
        "s",
        _load_stashes=lambda: {"s": {f"K{i}": "V" for i in range(50)}},
        _load_history=lambda: [{"stash": "s"} for _ in range(100)],
        _load_favorites=lambda: ["s"],
        _load_ratings=lambda: {"s": 5},
        _load_tags=lambda: {"s": ["a", "b"]},
    )
    assert result.score == 100.0


def test_grade_function():
    assert _grade(85) == "A"
    assert _grade(65) == "B"
    assert _grade(45) == "C"
    assert _grade(25) == "D"
    assert _grade(10) == "F"


def test_no_signals_for_empty_stash():
    result = compute_reputation(
        "empty",
        _load_stashes=lambda: {"empty": {}},
        _load_history=lambda: [],
        _load_favorites=lambda: [],
        _load_ratings=lambda: {},
        _load_tags=lambda: {},
    )
    assert result.score == 0.0
    assert result.signals == []
