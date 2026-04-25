"""Tests for stashpoint.bookmark."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from stashpoint.bookmark import (
    add_bookmark,
    remove_bookmark,
    is_bookmarked,
    list_bookmarks,
    load_bookmarks,
    save_bookmarks,
    StashNotFoundError,
    AlreadyBookmarkedError,
)


@pytest.fixture
def mock_bookmarks(tmp_path, monkeypatch):
    bookmark_file = tmp_path / "bookmarks.json"
    monkeypatch.setattr("stashpoint.bookmark.get_bookmark_path", lambda: bookmark_file)
    return bookmark_file


@pytest.fixture
def mock_stashes():
    stashes = {"dev": {"FOO": "bar"}, "prod": {"ENV": "production"}}
    with patch("stashpoint.bookmark.load_stashes", return_value=stashes):
        yield stashes


def test_load_bookmarks_empty(mock_bookmarks):
    result = load_bookmarks()
    assert result == []


def test_add_bookmark(mock_bookmarks, mock_stashes):
    add_bookmark("dev")
    result = load_bookmarks()
    assert "dev" in result


def test_add_bookmark_stash_not_found(mock_bookmarks, mock_stashes):
    with pytest.raises(StashNotFoundError):
        add_bookmark("nonexistent")


def test_add_bookmark_already_bookmarked(mock_bookmarks, mock_stashes):
    add_bookmark("dev")
    with pytest.raises(AlreadyBookmarkedError):
        add_bookmark("dev")


def test_remove_bookmark_returns_true(mock_bookmarks, mock_stashes):
    add_bookmark("dev")
    result = remove_bookmark("dev")
    assert result is True
    assert "dev" not in load_bookmarks()


def test_remove_bookmark_not_present_returns_false(mock_bookmarks):
    result = remove_bookmark("ghost")
    assert result is False


def test_is_bookmarked_true(mock_bookmarks, mock_stashes):
    add_bookmark("prod")
    assert is_bookmarked("prod") is True


def test_is_bookmarked_false(mock_bookmarks):
    assert is_bookmarked("dev") is False


def test_list_bookmarks_order_preserved(mock_bookmarks, mock_stashes):
    add_bookmark("dev")
    add_bookmark("prod")
    result = list_bookmarks()
    assert result == ["dev", "prod"]


def test_save_and_load_roundtrip(mock_bookmarks):
    save_bookmarks(["alpha", "beta"])
    result = load_bookmarks()
    assert result == ["alpha", "beta"]
