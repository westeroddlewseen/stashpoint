"""Tests for stashpoint.storage module."""

import json
import os
import pytest
from pathlib import Path

from stashpoint.storage import (
    delete_stash,
    list_stashes,
    load_stash,
    load_stashes,
    save_stash,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    """Redirect stash storage to a temp directory for each test."""
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def test_load_stashes_empty():
    assert load_stashes() == {}


def test_save_and_load_stash():
    save_stash("myproject", {"API_KEY": "abc123", "DEBUG": "true"})
    result = load_stash("myproject")
    assert result == {"API_KEY": "abc123", "DEBUG": "true"}


def test_load_stash_not_found():
    with pytest.raises(KeyError, match="No stash found with name 'missing'"):
        load_stash("missing")


def test_save_stash_overwrites_existing():
    save_stash("env", {"FOO": "bar"})
    save_stash("env", {"FOO": "baz", "NEW": "val"})
    result = load_stash("env")
    assert result == {"FOO": "baz", "NEW": "val"}


def test_delete_stash():
    save_stash("temp", {"X": "1"})
    delete_stash("temp")
    assert "temp" not in load_stashes()


def test_delete_stash_not_found():
    with pytest.raises(KeyError, match="No stash found with name 'ghost'"):
        delete_stash("ghost")


def test_list_stashes_sorted():
    save_stash("zebra", {})
    save_stash("alpha", {})
    save_stash("middle", {})
    assert list_stashes() == ["alpha", "middle", "zebra"]


def test_list_stashes_empty():
    assert list_stashes() == []


def test_stash_file_is_valid_json(isolated_stash_dir):
    save_stash("proj", {"KEY": "value"})
    stash_file = isolated_stash_dir / "stashes.json"
    with open(stash_file) as f:
        data = json.load(f)
    assert "proj" in data
