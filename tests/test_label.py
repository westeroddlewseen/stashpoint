"""Tests for stashpoint.label module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from stashpoint.label import (
    set_label,
    get_label,
    remove_label,
    list_labels,
    StashNotFoundError,
    LabelNotFoundError,
)


SAMPLE_STASHES = {"myproject": {"DB_HOST": "localhost"}, "staging": {"DB_HOST": "staging-db"}}


@pytest.fixture()
def mock_labels(tmp_path, monkeypatch):
    label_file = tmp_path / "labels.json"

    def _get_label_path():
        return label_file

    monkeypatch.setattr("stashpoint.label.get_label_path", _get_label_path)
    monkeypatch.setattr("stashpoint.label.load_stashes", lambda: SAMPLE_STASHES)
    return label_file


def test_get_label_missing_returns_none(mock_labels):
    assert get_label("myproject") is None


def test_set_and_get_label(mock_labels):
    set_label("myproject", "My Project DB")
    assert get_label("myproject") == "My Project DB"


def test_set_label_stash_not_found(mock_labels):
    with pytest.raises(StashNotFoundError):
        set_label("nonexistent", "Some Label")


def test_set_label_no_stash_check(mock_labels):
    # Should not raise even if stash doesn't exist when check_exists=False
    set_label("ghost", "Ghost Label", check_exists=False)
    assert get_label("ghost") == "Ghost Label"


def test_set_label_overwrites_existing(mock_labels):
    set_label("myproject", "First Label")
    set_label("myproject", "Updated Label")
    assert get_label("myproject") == "Updated Label"


def test_remove_label(mock_labels):
    set_label("myproject", "To Remove")
    remove_label("myproject")
    assert get_label("myproject") is None


def test_remove_label_not_found_raises(mock_labels):
    with pytest.raises(LabelNotFoundError):
        remove_label("myproject")


def test_list_labels_empty(mock_labels):
    assert list_labels() == {}


def test_list_labels_returns_all(mock_labels):
    set_label("myproject", "Project A")
    set_label("staging", "Staging Env")
    result = list_labels()
    assert result == {"myproject": "Project A", "staging": "Staging Env"}


def test_labels_persisted_to_disk(mock_labels, tmp_path):
    label_file = tmp_path / "labels.json"
    set_label("myproject", "Persisted Label")
    assert label_file.exists()
    data = json.loads(label_file.read_text())
    assert data["myproject"] == "Persisted Label"
