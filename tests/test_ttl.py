"""Tests for stashpoint.ttl"""

import time
import pytest
from unittest.mock import patch, MagicMock
from stashpoint import ttl as ttl_mod
from stashpoint.ttl import (
    set_ttl,
    get_ttl,
    clear_ttl,
    is_expired,
    list_expired,
    StashNotFoundError,
    InvalidTTLError,
)


@pytest.fixture
def mock_stashes():
    stashes = {"myenv": {"FOO": "bar"}, "prod": {"DB": "postgres"}}
    with patch("stashpoint.ttl.load_stashes", return_value=stashes):
        yield stashes


@pytest.fixture
def mock_ttl_store(tmp_path, monkeypatch):
    ttl_file = tmp_path / "ttl.json"
    monkeypatch.setattr(ttl_mod, "get_ttl_path", lambda: ttl_file)
    yield ttl_file


def test_set_ttl_returns_future_timestamp(mock_stashes, mock_ttl_store):
    before = time.time()
    expires_at = set_ttl("myenv", 60)
    after = time.time()
    assert before + 60 <= expires_at <= after + 60


def test_set_ttl_stores_entry(mock_stashes, mock_ttl_store):
    set_ttl("myenv", 120)
    entry = get_ttl("myenv")
    assert entry is not None
    assert entry["seconds"] == 120
    assert "expires_at" in entry


def test_set_ttl_stash_not_found(mock_stashes, mock_ttl_store):
    with pytest.raises(StashNotFoundError):
        set_ttl("nonexistent", 60)


def test_set_ttl_invalid_zero(mock_stashes, mock_ttl_store):
    with pytest.raises(InvalidTTLError):
        set_ttl("myenv", 0)


def test_set_ttl_invalid_negative(mock_stashes, mock_ttl_store):
    with pytest.raises(InvalidTTLError):
        set_ttl("myenv", -30)


def test_get_ttl_missing_returns_none(mock_ttl_store):
    result = get_ttl("ghost")
    assert result is None


def test_clear_ttl_removes_entry(mock_stashes, mock_ttl_store):
    set_ttl("myenv", 60)
    removed = clear_ttl("myenv")
    assert removed is True
    assert get_ttl("myenv") is None


def test_clear_ttl_returns_false_when_not_set(mock_ttl_store):
    result = clear_ttl("nope")
    assert result is False


def test_is_expired_false_for_future_ttl(mock_stashes, mock_ttl_store):
    set_ttl("myenv", 9999)
    assert is_expired("myenv") is False


def test_is_expired_true_for_past_ttl(mock_ttl_store):
    import json
    data = {"myenv": {"seconds": 1, "expires_at": time.time() - 10}}
    mock_ttl_store.write_text(json.dumps(data))
    assert is_expired("myenv") is True


def test_is_expired_false_when_no_ttl(mock_ttl_store):
    assert is_expired("anything") is False


def test_list_expired_returns_expired_names(mock_ttl_store):
    import json
    now = time.time()
    data = {
        "old": {"seconds": 1, "expires_at": now - 5},
        "fresh": {"seconds": 9999, "expires_at": now + 9999},
    }
    mock_ttl_store.write_text(json.dumps(data))
    expired = list_expired()
    assert "old" in expired
    assert "fresh" not in expired
