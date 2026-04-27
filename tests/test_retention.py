"""Tests for stashpoint.retention."""

from __future__ import annotations

import time
from unittest.mock import patch, MagicMock

import pytest

from stashpoint.retention import (
    set_retention,
    clear_retention,
    get_retention,
    list_expired,
    StashNotFoundError,
    InvalidRetentionError,
    MAX_RETENTION_DAYS,
)


@pytest.fixture()
def mock_stashes():
    with patch("stashpoint.retention.load_stashes", return_value={"myenv": {"A": "1"}}):
        yield


@pytest.fixture()
def mock_store():
    store: dict = {}
    with patch("stashpoint.retention.load_retention", side_effect=lambda: dict(store)), \
         patch("stashpoint.retention.save_retention", side_effect=lambda d: store.update(d) or store.__class__(d)):
        # Ensure save replaces contents
        def _save(d):
            store.clear()
            store.update(d)
        with patch("stashpoint.retention.save_retention", side_effect=_save):
            yield store


def test_set_retention_returns_future_timestamp(mock_stashes, mock_store):
    before = int(time.time())
    expiry = set_retention("myenv", 30)
    after = int(time.time())
    assert before + 30 * 86400 <= expiry <= after + 30 * 86400


def test_set_retention_stores_value(mock_stashes, mock_store):
    set_retention("myenv", 7)
    assert "myenv" in mock_store


def test_set_retention_stash_not_found():
    with patch("stashpoint.retention.load_stashes", return_value={}):
        with pytest.raises(StashNotFoundError):
            set_retention("ghost", 10)


def test_set_retention_invalid_zero(mock_stashes, mock_store):
    with pytest.raises(InvalidRetentionError):
        set_retention("myenv", 0)


def test_set_retention_invalid_negative(mock_stashes, mock_store):
    with pytest.raises(InvalidRetentionError):
        set_retention("myenv", -5)


def test_set_retention_exceeds_max(mock_stashes, mock_store):
    with pytest.raises(InvalidRetentionError):
        set_retention("myenv", MAX_RETENTION_DAYS + 1)


def test_clear_retention_removes_entry(mock_stashes, mock_store):
    set_retention("myenv", 5)
    result = clear_retention("myenv")
    assert result is True
    assert get_retention("myenv") is None


def test_clear_retention_returns_false_if_not_set(mock_store):
    result = clear_retention("nonexistent")
    assert result is False


def test_get_retention_returns_none_when_missing(mock_store):
    assert get_retention("unknown") is None


def test_list_expired_returns_expired_names(mock_store):
    past = int(time.time()) - 100
    future = int(time.time()) + 100000
    mock_store.update({"old": past, "new": future})
    expired = list_expired()
    assert "old" in expired
    assert "new" not in expired


def test_list_expired_filters_by_provided_names(mock_store):
    past = int(time.time()) - 1
    mock_store.update({"a": past, "b": past})
    expired = list_expired(stash_names=["a"])
    assert "a" in expired
    assert "b" not in expired
