"""Tests for stashpoint.visibility module."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from stashpoint.visibility import (
    VISIBILITY_LEVELS,
    InvalidVisibilityError,
    StashNotFoundError,
    get_visibility,
    list_by_visibility,
    remove_visibility,
    set_visibility,
)


@pytest.fixture
def mock_vis(tmp_path, monkeypatch):
    vis_file = tmp_path / "visibility.json"

    def _get_path():
        return vis_file

    monkeypatch.setattr("stashpoint.visibility.get_visibility_path", _get_path)
    return vis_file


def test_get_visibility_default(mock_vis):
    assert get_visibility("myproject") == "private"


def test_set_and_get_visibility(mock_vis):
    set_visibility("myproject", "public")
    assert get_visibility("myproject") == "public"


def test_set_visibility_shared(mock_vis):
    set_visibility("alpha", "shared")
    assert get_visibility("alpha") == "shared"


def test_set_visibility_invalid_level(mock_vis):
    with pytest.raises(InvalidVisibilityError):
        set_visibility("myproject", "secret")


def test_set_visibility_stash_not_found(mock_vis):
    with pytest.raises(StashNotFoundError):
        set_visibility("ghost", "public", stashes={})


def test_set_visibility_with_valid_stash(mock_vis):
    stashes = {"prod": {"KEY": "val"}}
    set_visibility("prod", "shared", stashes=stashes)
    assert get_visibility("prod") == "shared"


def test_remove_visibility_existing(mock_vis):
    set_visibility("alpha", "public")
    result = remove_visibility("alpha")
    assert result is True
    assert get_visibility("alpha") == "private"


def test_remove_visibility_not_set(mock_vis):
    result = remove_visibility("nonexistent")
    assert result is False


def test_list_by_visibility_empty(mock_vis):
    assert list_by_visibility("public") == []


def test_list_by_visibility_returns_matching(mock_vis):
    set_visibility("a", "public")
    set_visibility("b", "shared")
    set_visibility("c", "public")
    result = list_by_visibility("public")
    assert result == ["a", "c"]


def test_list_by_visibility_sorted(mock_vis):
    set_visibility("z", "shared")
    set_visibility("a", "shared")
    set_visibility("m", "shared")
    result = list_by_visibility("shared")
    assert result == ["a", "m", "z"]


def test_list_by_visibility_invalid_level(mock_vis):
    with pytest.raises(InvalidVisibilityError):
        list_by_visibility("unknown")


def test_visibility_levels_constant():
    assert set(VISIBILITY_LEVELS) == {"private", "shared", "public"}
