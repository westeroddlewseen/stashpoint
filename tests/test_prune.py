"""Tests for stashpoint.prune module."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import pytest

from stashpoint.prune import prune_stashes, format_prune_summary, get_stash_last_used


SAMPLE_STASHES = {
    "dev": {"DB_HOST": "localhost", "DEBUG": "1"},
    "prod": {"DB_HOST": "prod.db", "DEBUG": "0"},
    "old": {"LEGACY": "true"},
}


@pytest.fixture
def mock_deps(monkeypatch):
    monkeypatch.setattr("stashpoint.prune.load_stashes", lambda: dict(SAMPLE_STASHES))
    saved = {}

    def _save(s):
        saved.update(s)

    monkeypatch.setattr("stashpoint.prune.save_stashes", _save)
    monkeypatch.setattr("stashpoint.prune.is_locked", lambda name: False)
    monkeypatch.setattr("stashpoint.prune.is_pinned", lambda name: False)
    monkeypatch.setattr("stashpoint.prune.load_history", lambda: [])
    return saved


def test_prune_specific_names(mock_deps):
    pruned = prune_stashes(names=["dev", "old"])
    assert "dev" in pruned
    assert "old" in pruned
    assert "prod" not in pruned


def test_prune_dry_run_does_not_save(monkeypatch):
    monkeypatch.setattr("stashpoint.prune.load_stashes", lambda: dict(SAMPLE_STASHES))
    save_called = []
    monkeypatch.setattr("stashpoint.prune.save_stashes", lambda s: save_called.append(s))
    monkeypatch.setattr("stashpoint.prune.is_locked", lambda name: False)
    monkeypatch.setattr("stashpoint.prune.is_pinned", lambda name: False)
    monkeypatch.setattr("stashpoint.prune.load_history", lambda: [])

    pruned = prune_stashes(dry_run=True, names=["dev"])
    assert "dev" in pruned
    assert save_called == []


def test_prune_skips_locked(monkeypatch):
    monkeypatch.setattr("stashpoint.prune.load_stashes", lambda: dict(SAMPLE_STASHES))
    monkeypatch.setattr("stashpoint.prune.save_stashes", lambda s: None)
    monkeypatch.setattr("stashpoint.prune.is_locked", lambda name: name == "prod")
    monkeypatch.setattr("stashpoint.prune.is_pinned", lambda name: False)
    monkeypatch.setattr("stashpoint.prune.load_history", lambda: [])

    pruned = prune_stashes()
    assert "prod" not in pruned


def test_prune_skips_pinned(monkeypatch):
    monkeypatch.setattr("stashpoint.prune.load_stashes", lambda: dict(SAMPLE_STASHES))
    monkeypatch.setattr("stashpoint.prune.save_stashes", lambda s: None)
    monkeypatch.setattr("stashpoint.prune.is_locked", lambda name: False)
    monkeypatch.setattr("stashpoint.prune.is_pinned", lambda name: name == "dev")
    monkeypatch.setattr("stashpoint.prune.load_history", lambda: [])

    pruned = prune_stashes()
    assert "dev" not in pruned


def test_prune_older_than_days_filters_recent(monkeypatch):
    now = datetime.now(timezone.utc)
    recent_ts = (now - timedelta(days=2)).isoformat()
    old_ts = (now - timedelta(days=30)).isoformat()

    history = [
        {"stash": "dev", "timestamp": recent_ts},
        {"stash": "old", "timestamp": old_ts},
    ]

    monkeypatch.setattr("stashpoint.prune.load_stashes", lambda: dict(SAMPLE_STASHES))
    monkeypatch.setattr("stashpoint.prune.save_stashes", lambda s: None)
    monkeypatch.setattr("stashpoint.prune.is_locked", lambda name: False)
    monkeypatch.setattr("stashpoint.prune.is_pinned", lambda name: False)
    monkeypatch.setattr("stashpoint.prune.load_history", lambda: history)

    pruned = prune_stashes(older_than_days=10)
    assert "dev" not in pruned
    assert "old" in pruned


def test_prune_nonexistent_name_ignored(mock_deps):
    pruned = prune_stashes(names=["ghost"])
    assert pruned == []


def test_format_prune_summary_empty():
    result = format_prune_summary([])
    assert "No stashes" in result


def test_format_prune_summary_with_names():
    result = format_prune_summary(["dev", "old"])
    assert "Removed 2 stash" in result
    assert "dev" in result
    assert "old" in result


def test_format_prune_summary_dry_run():
    result = format_prune_summary(["dev"], dry_run=True)
    assert "dry-run" in result
    assert "dev" in result
