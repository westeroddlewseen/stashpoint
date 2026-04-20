"""Tests for stashpoint.snapshot module."""

import os
import pytest

from stashpoint.snapshot import capture_env, snapshot, StashAlreadyExistsError
from stashpoint.storage import load_stash, save_stash


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    return tmp_path


def test_capture_env_returns_dict(monkeypatch):
    monkeypatch.setenv("MY_VAR", "hello")
    result = capture_env()
    assert isinstance(result, dict)
    assert result["MY_VAR"] == "hello"


def test_capture_env_with_prefix(monkeypatch):
    monkeypatch.setenv("APP_HOST", "localhost")
    monkeypatch.setenv("APP_PORT", "8080")
    monkeypatch.setenv("OTHER_VAR", "ignored")
    result = capture_env(prefix="APP_")
    assert "APP_HOST" in result
    assert "APP_PORT" in result
    assert "OTHER_VAR" not in result


def test_capture_env_no_prefix_includes_all(monkeypatch):
    monkeypatch.setenv("ALPHA", "1")
    monkeypatch.setenv("BETA", "2")
    result = capture_env()
    assert "ALPHA" in result
    assert "BETA" in result


def test_snapshot_saves_stash(monkeypatch):
    monkeypatch.setenv("SNAP_FOO", "bar")
    saved = snapshot("mysnap", prefix="SNAP_")
    assert saved["SNAP_FOO"] == "bar"
    loaded = load_stash("mysnap")
    assert loaded == {"SNAP_FOO": "bar"}


def test_snapshot_with_keys(monkeypatch):
    monkeypatch.setenv("KEY_A", "alpha")
    monkeypatch.setenv("KEY_B", "beta")
    monkeypatch.setenv("KEY_C", "gamma")
    saved = snapshot("keysnap", keys=["KEY_A", "KEY_C"])
    assert "KEY_A" in saved
    assert "KEY_C" in saved
    assert "KEY_B" not in saved
    loaded = load_stash("keysnap")
    assert loaded == {"KEY_A": "alpha", "KEY_C": "gamma"}


def test_snapshot_keys_missing_from_env(monkeypatch):
    monkeypatch.setenv("EXISTS", "yes")
    saved = snapshot("partial", keys=["EXISTS", "DOES_NOT_EXIST"])
    assert "EXISTS" in saved
    assert "DOES_NOT_EXIST" not in saved


def test_snapshot_raises_if_exists_no_overwrite(monkeypatch):
    monkeypatch.setenv("X", "1")
    save_stash("existing", {"X": "old"})
    with pytest.raises(StashAlreadyExistsError, match="existing"):
        snapshot("existing", keys=["X"])


def test_snapshot_overwrites_when_flag_set(monkeypatch):
    monkeypatch.setenv("X", "new_value")
    save_stash("overwritable", {"X": "old_value"})
    saved = snapshot("overwritable", keys=["X"], overwrite=True)
    assert saved["X"] == "new_value"
    loaded = load_stash("overwritable")
    assert loaded["X"] == "new_value"
