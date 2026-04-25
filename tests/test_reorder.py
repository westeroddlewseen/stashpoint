"""Tests for stashpoint.reorder."""

import pytest
from unittest.mock import patch

from stashpoint.reorder import (
    reorder_stash,
    get_reorder_summary,
    StashNotFoundError,
    InvalidKeyError,
)


SAMPLE = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}


def _mock_load(name):
    if name == "myenv":
        return dict(SAMPLE)
    return None


@patch("stashpoint.reorder.save_stash")
@patch("stashpoint.reorder.load_stash", side_effect=_mock_load)
def test_sort_alphabetically(mock_load, mock_save):
    result = reorder_stash("myenv", sort=True)
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]
    mock_save.assert_called_once_with("myenv", result)


@patch("stashpoint.reorder.save_stash")
@patch("stashpoint.reorder.load_stash", side_effect=_mock_load)
def test_sort_reverse(mock_load, mock_save):
    result = reorder_stash("myenv", sort=True, reverse=True)
    assert list(result.keys()) == ["ZEBRA", "MANGO", "APPLE"]


@patch("stashpoint.reorder.save_stash")
@patch("stashpoint.reorder.load_stash", side_effect=_mock_load)
def test_explicit_order(mock_load, mock_save):
    result = reorder_stash("myenv", order=["MANGO", "ZEBRA", "APPLE"])
    assert list(result.keys()) == ["MANGO", "ZEBRA", "APPLE"]


@patch("stashpoint.reorder.save_stash")
@patch("stashpoint.reorder.load_stash", side_effect=_mock_load)
def test_explicit_partial_order_appends_rest(mock_load, mock_save):
    result = reorder_stash("myenv", order=["MANGO"])
    assert list(result.keys())[0] == "MANGO"
    assert set(result.keys()) == {"ZEBRA", "APPLE", "MANGO"}


@patch("stashpoint.reorder.save_stash")
@patch("stashpoint.reorder.load_stash", side_effect=_mock_load)
def test_values_preserved(mock_load, mock_save):
    result = reorder_stash("myenv", sort=True)
    assert result["APPLE"] == "2"
    assert result["MANGO"] == "3"
    assert result["ZEBRA"] == "1"


@patch("stashpoint.reorder.load_stash", return_value=None)
def test_stash_not_found(mock_load):
    with pytest.raises(StashNotFoundError, match="missing"):
        reorder_stash("missing")


@patch("stashpoint.reorder.save_stash")
@patch("stashpoint.reorder.load_stash", side_effect=_mock_load)
def test_invalid_key_raises(mock_load, mock_save):
    with pytest.raises(InvalidKeyError, match="NOPE"):
        reorder_stash("myenv", order=["NOPE", "APPLE"])


def test_get_reorder_summary_detects_changes():
    original = {"A": "1", "B": "2", "C": "3"}
    reordered = {"C": "3", "A": "1", "B": "2"}
    lines = get_reorder_summary(original, reordered)
    assert any("C" in l for l in lines)


def test_get_reorder_summary_no_changes():
    original = {"A": "1", "B": "2"}
    lines = get_reorder_summary(original, original)
    assert lines == []
