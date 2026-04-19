"""Tests for stash locking."""

import pytest
from unittest.mock import patch
from pathlib import Path
from click.testing import CliRunner
from stashpoint.lock import lock_stash, unlock_stash, is_locked, load_locks
from stashpoint.cli_lock import lock_cmd


@pytest.fixture
def isolated_lock_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    with patch("stashpoint.lock.get_lock_path", return_value=tmp_path / "locks.json"):
        yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_is_locked_false_by_default(isolated_lock_dir):
    assert is_locked("myenv") is False


def test_lock_stash(isolated_lock_dir):
    lock_stash("myenv")
    assert is_locked("myenv") is True


def test_lock_stash_idempotent(isolated_lock_dir):
    lock_stash("myenv")
    lock_stash("myenv")
    assert load_locks().count("myenv") == 1


def test_unlock_stash(isolated_lock_dir):
    lock_stash("myenv")
    unlock_stash("myenv")
    assert is_locked("myenv") is False


def test_unlock_not_locked(isolated_lock_dir):
    unlock_stash("myenv")  # should not raise
    assert is_locked("myenv") is False


def test_cli_lock_add(runner, isolated_lock_dir):
    result = runner.invoke(lock_cmd, ["add", "prod"])
    assert result.exit_code == 0
    assert "locked" in result.output
    assert is_locked("prod")


def test_cli_lock_add_already_locked(runner, isolated_lock_dir):
    lock_stash("prod")
    result = runner.invoke(lock_cmd, ["add", "prod"])
    assert "already locked" in result.output


def test_cli_lock_remove(runner, isolated_lock_dir):
    lock_stash("prod")
    result = runner.invoke(lock_cmd, ["remove", "prod"])
    assert "unlocked" in result.output
    assert not is_locked("prod")


def test_cli_lock_list(runner, isolated_lock_dir):
    lock_stash("alpha")
    lock_stash("beta")
    result = runner.invoke(lock_cmd, ["list"])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_cli_lock_list_empty(runner, isolated_lock_dir):
    result = runner.invoke(lock_cmd, ["list"])
    assert "No locked stashes" in result.output
