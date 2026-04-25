"""Tests for stashpoint.remind and stashpoint.cli_remind."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from stashpoint.remind import (
    ReminderNotFoundError,
    StashNotFoundError,
    get_reminder,
    list_reminders,
    remove_reminder,
    set_reminder,
)
from stashpoint.cli_remind import remind_cmd


@pytest.fixture()
def mock_reminders(tmp_path, monkeypatch):
    """Isolate reminder storage to a temp directory."""
    reminder_file = tmp_path / "reminders.json"
    monkeypatch.setattr("stashpoint.remind.get_reminder_path", lambda: reminder_file)
    return reminder_file


@pytest.fixture()
def mock_stashes():
    return {"myapp": {"DB_URL": "postgres://localhost/dev"}, "ci": {}}


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_get_reminder_missing_returns_none(mock_reminders):
    assert get_reminder("nonexistent") is None


def test_set_and_get_reminder(mock_reminders, mock_stashes):
    with patch("stashpoint.remind.load_stashes", return_value=mock_stashes):
        set_reminder("myapp", "Remember to rotate the DB password!")
    assert get_reminder("myapp") == "Remember to rotate the DB password!"


def test_set_reminder_stash_not_found(mock_reminders, mock_stashes):
    with patch("stashpoint.remind.load_stashes", return_value=mock_stashes):
        with pytest.raises(StashNotFoundError):
            set_reminder("ghost", "hello")


def test_set_reminder_no_stash_check(mock_reminders):
    """check_stash=False should skip the stash existence check."""
    set_reminder("phantom", "spooky", check_stash=False)
    assert get_reminder("phantom") == "spooky"


def test_remove_reminder(mock_reminders):
    set_reminder("x", "msg", check_stash=False)
    remove_reminder("x")
    assert get_reminder("x") is None


def test_remove_reminder_not_found(mock_reminders):
    with pytest.raises(ReminderNotFoundError):
        remove_reminder("missing")


def test_list_reminders_sorted(mock_reminders):
    set_reminder("z_stash", "last", check_stash=False)
    set_reminder("a_stash", "first", check_stash=False)
    result = list_reminders()
    assert list(result.keys()) == ["a_stash", "z_stash"]


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_set_success(runner, mock_reminders, mock_stashes):
    with patch("stashpoint.remind.load_stashes", return_value=mock_stashes):
        result = runner.invoke(remind_cmd, ["set", "myapp", "Check credentials"])
    assert result.exit_code == 0
    assert "Reminder set" in result.output


def test_cli_set_stash_not_found(runner, mock_reminders, mock_stashes):
    with patch("stashpoint.remind.load_stashes", return_value=mock_stashes):
        result = runner.invoke(remind_cmd, ["set", "ghost", "hello"])
    assert result.exit_code == 1


def test_cli_get_existing(runner, mock_reminders):
    set_reminder("proj", "Update API key", check_stash=False)
    result = runner.invoke(remind_cmd, ["get", "proj"])
    assert "Update API key" in result.output


def test_cli_get_missing(runner, mock_reminders):
    result = runner.invoke(remind_cmd, ["get", "nope"])
    assert "No reminder" in result.output


def test_cli_remove_success(runner, mock_reminders):
    set_reminder("tmp", "bye", check_stash=False)
    result = runner.invoke(remind_cmd, ["remove", "tmp"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_list_empty(runner, mock_reminders):
    result = runner.invoke(remind_cmd, ["list"])
    assert "No reminders" in result.output


def test_cli_list_shows_entries(runner, mock_reminders):
    set_reminder("alpha", "msg1", check_stash=False)
    set_reminder("beta", "msg2", check_stash=False)
    result = runner.invoke(remind_cmd, ["list"])
    assert "alpha" in result.output
    assert "beta" in result.output
