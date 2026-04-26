"""Tests for stashpoint.rating"""

import pytest
from unittest.mock import patch

from stashpoint.rating import (
    InvalidRatingError,
    StashNotFoundError,
    get_rating,
    get_top_rated,
    rate_stash,
    remove_rating,
)


@pytest.fixture
def mock_stashes():
    stashes = {"prod": {"ENV": "production"}, "dev": {"ENV": "development"}, "staging": {}}
    with patch("stashpoint.rating.load_stashes", return_value=stashes):
        yield stashes


@pytest.fixture
def mock_ratings():
    store = {}

    def _load():
        return dict(store)

    def _save(data):
        store.clear()
        store.update(data)

    with patch("stashpoint.rating.load_ratings", side_effect=_load), \
         patch("stashpoint.rating.save_ratings", side_effect=_save):
        yield store


def test_rate_stash_stores_value(mock_stashes, mock_ratings):
    rate_stash("prod", 4)
    assert mock_ratings["prod"] == 4


def test_rate_stash_returns_rating(mock_stashes, mock_ratings):
    result = rate_stash("dev", 3)
    assert result == 3


def test_rate_stash_not_found(mock_stashes, mock_ratings):
    with pytest.raises(StashNotFoundError):
        rate_stash("nonexistent", 5)


def test_rate_stash_no_check_skips_existence(mock_ratings):
    rate_stash("ghost", 2, check_exists=False)
    assert mock_ratings["ghost"] == 2


def test_rate_stash_invalid_low(mock_stashes, mock_ratings):
    with pytest.raises(InvalidRatingError):
        rate_stash("prod", 0)


def test_rate_stash_invalid_high(mock_stashes, mock_ratings):
    with pytest.raises(InvalidRatingError):
        rate_stash("prod", 6)


def test_rate_stash_invalid_type(mock_stashes, mock_ratings):
    with pytest.raises(InvalidRatingError):
        rate_stash("prod", "five")  # type: ignore


def test_get_rating_returns_value(mock_ratings):
    mock_ratings["prod"] = 5
    assert get_rating("prod") == 5


def test_get_rating_unrated_returns_none(mock_ratings):
    assert get_rating("unrated") is None


def test_remove_rating_existing(mock_ratings):
    mock_ratings["dev"] = 3
    removed = remove_rating("dev")
    assert removed is True
    assert "dev" not in mock_ratings


def test_remove_rating_nonexistent(mock_ratings):
    removed = remove_rating("ghost")
    assert removed is False


def test_get_top_rated_sorted(mock_ratings):
    mock_ratings.update({"a": 3, "b": 5, "c": 1, "d": 4})
    top = get_top_rated()
    assert top[0] == ("b", 5)
    assert top[1] == ("d", 4)
    assert top[2] == ("a", 3)


def test_get_top_rated_respects_limit(mock_ratings):
    mock_ratings.update({"a": 5, "b": 4, "c": 3, "d": 2, "e": 1})
    top = get_top_rated(limit=2)
    assert len(top) == 2


def test_get_top_rated_empty(mock_ratings):
    assert get_top_rated() == []
