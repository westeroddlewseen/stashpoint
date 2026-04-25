"""Tests for stashpoint.chmod module."""

import pytest
from unittest.mock import patch, MagicMock

from stashpoint.chmod import (
    set_readonly,
    set_readwrite,
    is_readonly,
    list_readonly,
    StashNotFoundError,
    StashAlreadyReadOnlyError,
    StashNotReadOnlyError,
)


@pytest.fixture
def mock_chmod():
    store = {}

    def _load():
        return dict(store)

    def _save(data):
        store.clear()
        store.update(data)

    with patch("stashpoint.chmod.load_chmod", side_effect=_load), \
         patch("stashpoint.chmod.save_chmod", side_effect=_save):
        yield store


SAMPLE_STASHES = {"dev": {"KEY": "val"}, "prod": {"KEY": "other"}}


def test_is_readonly_false_by_default(mock_chmod):
    assert is_readonly("dev") is False


def test_set_readonly_marks_stash(mock_chmod):
    set_readonly("dev", SAMPLE_STASHES)
    assert is_readonly("dev") is True


def test_set_readonly_stash_not_found(mock_chmod):
    with pytest.raises(StashNotFoundError):
        set_readonly("missing", SAMPLE_STASHES)


def test_set_readonly_idempotent_raises(mock_chmod):
    set_readonly("dev", SAMPLE_STASHES)
    with pytest.raises(StashAlreadyReadOnlyError):
        set_readonly("dev", SAMPLE_STASHES)


def test_set_readwrite_removes_readonly(mock_chmod):
    set_readonly("dev", SAMPLE_STASHES)
    set_readwrite("dev", SAMPLE_STASHES)
    assert is_readonly("dev") is False


def test_set_readwrite_on_non_readonly_raises(mock_chmod):
    with pytest.raises(StashNotReadOnlyError):
        set_readwrite("dev", SAMPLE_STASHES)


def test_set_readwrite_stash_not_found(mock_chmod):
    with pytest.raises(StashNotFoundError):
        set_readwrite("missing", SAMPLE_STASHES)


def test_list_readonly_empty(mock_chmod):
    assert list_readonly() == []


def test_list_readonly_returns_sorted(mock_chmod):
    set_readonly("prod", SAMPLE_STASHES)
    set_readonly("dev", SAMPLE_STASHES)
    assert list_readonly() == ["dev", "prod"]


def test_readonly_does_not_affect_other_stash(mock_chmod):
    set_readonly("dev", SAMPLE_STASHES)
    assert is_readonly("prod") is False
