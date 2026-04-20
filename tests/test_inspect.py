"""Tests for stashpoint.inspect module."""

import pytest
from unittest.mock import patch

from stashpoint.inspect import inspect_stash, format_inspect, StashNotFoundError


SAMPLE_VARS = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}

SAMPLE_HISTORY = [
    {"event": "save", "stash": "myproject", "timestamp": "2024-06-01T12:00:00"},
    {"event": "load", "stash": "myproject", "timestamp": "2024-06-02T09:30:00"},
]


@pytest.fixture
def mock_deps():
    with patch("stashpoint.inspect.load_stash", return_value=SAMPLE_VARS) as ml, \
         patch("stashpoint.inspect.is_locked", return_value=False) as mi, \
         patch("stashpoint.inspect.get_tags", return_value=["prod", "web"]) as mt, \
         patch("stashpoint.inspect.get_stash_history", return_value=SAMPLE_HISTORY) as mh:
        yield {"load_stash": ml, "is_locked": mi, "get_tags": mt, "get_history": mh}


def test_inspect_returns_name(mock_deps):
    report = inspect_stash("myproject")
    assert report["name"] == "myproject"


def test_inspect_variable_count(mock_deps):
    report = inspect_stash("myproject")
    assert report["variable_count"] == 3


def test_inspect_variables_sorted(mock_deps):
    report = inspect_stash("myproject")
    assert report["variables"] == ["API_KEY", "DB_HOST", "DB_PORT"]


def test_inspect_tags_sorted(mock_deps):
    report = inspect_stash("myproject")
    assert report["tags"] == ["prod", "web"]


def test_inspect_locked_false(mock_deps):
    report = inspect_stash("myproject")
    assert report["locked"] is False


def test_inspect_locked_true(mock_deps):
    mock_deps["is_locked"].return_value = True
    report = inspect_stash("myproject")
    assert report["locked"] is True


def test_inspect_last_modified_parsed(mock_deps):
    report = inspect_stash("myproject")
    assert report["last_modified"] == "2024-06-02 09:30:00"


def test_inspect_history_entries_count(mock_deps):
    report = inspect_stash("myproject")
    assert report["history_entries"] == 2


def test_inspect_no_history(mock_deps):
    mock_deps["get_history"].return_value = []
    report = inspect_stash("myproject")
    assert report["last_modified"] is None
    assert report["history_entries"] == 0


def test_inspect_stash_not_found():
    with patch("stashpoint.inspect.load_stash", return_value=None):
        with pytest.raises(StashNotFoundError, match="myproject"):
            inspect_stash("myproject")


def test_format_inspect_contains_name(mock_deps):
    report = inspect_stash("myproject")
    output = format_inspect(report)
    assert "myproject" in output


def test_format_inspect_shows_variable_names(mock_deps):
    report = inspect_stash("myproject")
    output = format_inspect(report)
    assert "API_KEY" in output
    assert "DB_HOST" in output


def test_format_inspect_shows_tags(mock_deps):
    report = inspect_stash("myproject")
    output = format_inspect(report)
    assert "prod" in output
    assert "web" in output


def test_format_inspect_no_tags(mock_deps):
    mock_deps["get_tags"].return_value = []
    report = inspect_stash("myproject")
    output = format_inspect(report)
    assert "(none)" in output
