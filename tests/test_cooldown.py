"""Tests for stashpoint.cooldown."""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from stashpoint.cooldown import (
    CooldownActiveError,
    StashNotFoundError,
    check_cooldown,
    clear_cooldown,
    enforce_cooldown,
    record_write,
    set_cooldown,
)


@pytest.fixture()
def mock_stashes(tmp_path, monkeypatch):
    stash_file = tmp_path / "stashes.json"
    stash_file.write_text(json.dumps({"myapp": {"KEY": "val"}}))
    monkeypatch.setattr("stashpoint.cooldown.get_stash_path", lambda: stash_file)
    monkeypatch.setattr(
        "stashpoint.cooldown.load_stashes", lambda: {"myapp": {"KEY": "val"}}
    )
    cooldown_file = tmp_path / "cooldowns.json"
    monkeypatch.setattr(
        "stashpoint.cooldown.get_cooldown_path", lambda: cooldown_file
    )
    return tmp_path


def test_set_cooldown_stores_entry(mock_stashes):
    set_cooldown("myapp", 60)
    data = json.loads((mock_stashes / "cooldowns.json").read_text())
    assert data["myapp"]["interval"] == 60
    assert data["myapp"]["last_write"] is None


def test_set_cooldown_stash_not_found(mock_stashes):
    with pytest.raises(StashNotFoundError):
        set_cooldown("ghost", 30)


def test_set_cooldown_invalid_seconds(mock_stashes):
    with pytest.raises(ValueError):
        set_cooldown("myapp", 0)


def test_clear_cooldown_returns_true(mock_stashes):
    set_cooldown("myapp", 10)
    result = clear_cooldown("myapp")
    assert result is True


def test_clear_cooldown_missing_returns_false(mock_stashes):
    result = clear_cooldown("nothing")
    assert result is False


def test_check_cooldown_no_entry_returns_none(mock_stashes):
    assert check_cooldown("myapp") is None


def test_check_cooldown_no_last_write_returns_none(mock_stashes):
    set_cooldown("myapp", 60)
    assert check_cooldown("myapp") is None


def test_record_write_then_check_returns_remaining(mock_stashes):
    set_cooldown("myapp", 3600)
    record_write("myapp")
    remaining = check_cooldown("myapp")
    assert remaining is not None
    assert 3598 < remaining <= 3600


def test_check_cooldown_expired_returns_none(mock_stashes):
    set_cooldown("myapp", 1)
    data = json.loads((mock_stashes / "cooldowns.json").read_text())
    data["myapp"]["last_write"] = time.time() - 5
    (mock_stashes / "cooldowns.json").write_text(json.dumps(data))
    assert check_cooldown("myapp") is None


def test_enforce_cooldown_raises_when_active(mock_stashes):
    set_cooldown("myapp", 3600)
    record_write("myapp")
    with pytest.raises(CooldownActiveError) as exc_info:
        enforce_cooldown("myapp")
    assert "myapp" in str(exc_info.value)


def test_enforce_cooldown_passes_when_inactive(mock_stashes):
    set_cooldown("myapp", 1)
    data = json.loads((mock_stashes / "cooldowns.json").read_text())
    data["myapp"]["last_write"] = time.time() - 10
    (mock_stashes / "cooldowns.json").write_text(json.dumps(data))
    enforce_cooldown("myapp")  # should not raise
