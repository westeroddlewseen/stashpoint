"""Tests for stashpoint.favorite."""

import json
import pytest
from unittest.mock import patch, MagicMock
from stashpoint.favorite import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
    load_favorites,
    save_favorites,
    StashNotFoundError,
    AlreadyFavoritedError,
)

SAMPLE_STASHES = {"dev": {"API_KEY": "abc"}, "prod": {"API_KEY": "xyz"}}


@pytest.fixture
def mock_favorites(tmp_path, monkeypatch):
    fav_file = tmp_path / "favorites.json"
    monkeypatch.setattr("stashpoint.favorite.get_favorite_path", lambda: fav_file)
    return fav_file


def test_load_favorites_empty(mock_favorites):
    result = load_favorites()
    assert result == []


def test_add_favorite(mock_favorites):
    add_favorite("dev", SAMPLE_STASHES)
    assert "dev" in load_favorites()


def test_add_favorite_stash_not_found(mock_favorites):
    with pytest.raises(StashNotFoundError):
        add_favorite("missing", SAMPLE_STASHES)


def test_add_favorite_already_exists_raises(mock_favorites):
    add_favorite("dev", SAMPLE_STASHES)
    with pytest.raises(AlreadyFavoritedError):
        add_favorite("dev", SAMPLE_STASHES)


def test_add_favorite_overwrite_does_not_raise(mock_favorites):
    add_favorite("dev", SAMPLE_STASHES)
    add_favorite("dev", SAMPLE_STASHES, overwrite=True)
    assert load_favorites().count("dev") == 1


def test_remove_favorite_returns_true(mock_favorites):
    add_favorite("dev", SAMPLE_STASHES)
    result = remove_favorite("dev")
    assert result is True
    assert "dev" not in load_favorites()


def test_remove_favorite_not_present_returns_false(mock_favorites):
    result = remove_favorite("dev")
    assert result is False


def test_list_favorites_sorted(mock_favorites):
    add_favorite("prod", SAMPLE_STASHES)
    add_favorite("dev", SAMPLE_STASHES)
    result = list_favorites()
    assert result == sorted(result)


def test_is_favorite_true(mock_favorites):
    add_favorite("dev", SAMPLE_STASHES)
    assert is_favorite("dev") is True


def test_is_favorite_false(mock_favorites):
    assert is_favorite("dev") is False


def test_save_favorites_deduplicates(mock_favorites):
    save_favorites(["dev", "dev", "prod"])
    result = load_favorites()
    assert result.count("dev") == 1
