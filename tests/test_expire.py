"""Tests for stashpoint.expire."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from stashpoint.expire import (
    StashNotFoundError,
    clear_expiry,
    get_expiry,
    is_expired,
    purge_expired,
    set_expiry,
)


SAMPLE_STASHES = {"myproject": {"KEY": "val"}, "other": {"X": "1"}}


@pytest.fixture(autouse=True)
def mock_deps(tmp_path):
    stashes = dict(SAMPLE_STASHES)
    expiry: dict = {}

    with (
        patch("stashpoint.expire.load_stashes", return_value=stashes),
        patch("stashpoint.expire.save_stashes", side_effect=lambda d: stashes.update(d) or stashes.clear() or stashes.update(d)),
        patch("stashpoint.expire.load_expiry", side_effect=lambda: dict(expiry)),
        patch("stashpoint.expire.save_expiry", side_effect=lambda d: (expiry.clear(), expiry.update(d))),
        patch("stashpoint.expire.get_expiry_path"),
    ):
        yield expiry


def test_set_expiry_returns_future_timestamp(mock_deps):
    ts = set_expiry("myproject", 3600)
    assert ts > time.time()


def test_set_expiry_stores_value(mock_deps):
    set_expiry("myproject", 100)
    ts = get_expiry("myproject")
    assert ts is not None
    assert ts > time.time()


def test_set_expiry_stash_not_found(mock_deps):
    with pytest.raises(StashNotFoundError):
        set_expiry("nonexistent", 60)


def test_clear_expiry_removes_entry(mock_deps):
    set_expiry("myproject", 100)
    result = clear_expiry("myproject")
    assert result is True
    assert get_expiry("myproject") is None


def test_clear_expiry_no_entry_returns_false(mock_deps):
    result = clear_expiry("myproject")
    assert result is False


def test_is_expired_false_for_future(mock_deps):
    set_expiry("myproject", 9999)
    assert is_expired("myproject") is False


def test_is_expired_true_for_past(mock_deps):
    set_expiry("myproject", -1)
    assert is_expired("myproject") is True


def test_is_expired_false_when_no_expiry(mock_deps):
    assert is_expired("myproject") is False


def test_purge_expired_removes_expired(mock_deps):
    set_expiry("myproject", -1)
    purged = purge_expired()
    assert "myproject" in purged


def test_purge_expired_keeps_active(mock_deps):
    set_expiry("myproject", 9999)
    purged = purge_expired()
    assert "myproject" not in purged


def test_purge_expired_returns_empty_when_none(mock_deps):
    purged = purge_expired()
    assert purged == []
