"""Tests for stashpoint.history module."""

import os
import pytest
from unittest.mock import patch

from stashpoint import history as hist


@pytest.fixture(autouse=True)
def isolated_history(tmp_path):
    history_file = tmp_path / "history.json"
    with patch("stashpoint.history.get_history_path", return_value=str(history_file)):
        yield tmp_path


def test_load_history_empty():
    assert hist.load_history() == []


def test_record_event_saves_entry():
    hist.record_event("save", "myproject", {"FOO": "bar"})
    entries = hist.load_history()
    assert len(entries) == 1
    assert entries[0]["action"] == "save"
    assert entries[0]["stash"] == "myproject"
    assert entries[0]["variables"] == {"FOO": "bar"}
    assert "timestamp" in entries[0]


def test_record_multiple_events():
    hist.record_event("save", "proj", {"A": "1"})
    hist.record_event("load", "proj", {"A": "1"})
    entries = hist.load_history()
    assert len(entries) == 2
    assert entries[1]["action"] == "load"


def test_get_stash_history_filters_by_name():
    hist.record_event("save", "alpha", {})
    hist.record_event("save", "beta", {})
    hist.record_event("load", "alpha", {})
    result = hist.get_stash_history("alpha")
    assert len(result) == 2
    assert all(e["stash"] == "alpha" for e in result)


def test_get_stash_history_not_found():
    hist.record_event("save", "other", {})
    assert hist.get_stash_history("missing") == []


def test_clear_history():
    hist.record_event("save", "x", {})
    hist.clear_history()
    assert hist.load_history() == []


def test_record_event_no_variables():
    hist.record_event("delete", "gone")
    entries = hist.load_history()
    assert entries[0]["variables"] == {}
