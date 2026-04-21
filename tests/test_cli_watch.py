"""Tests for stashpoint.cli_watch."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from stashpoint.cli_watch import watch_cmd
from stashpoint.watch import StashNotFoundError


@pytest.fixture
def runner():
    return CliRunner()


def test_start_stash_not_found(runner):
    with patch("stashpoint.cli_watch.poll_stash", side_effect=StashNotFoundError("Stash 'x' not found.")):
        result = runner.invoke(watch_cmd, ["start", "x"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_start_prints_changes(runner):
    def fake_poll(name, interval, max_polls, on_change):
        on_change(name, {"A": "old"}, {"A": "new", "B": "added"})

    with patch("stashpoint.cli_watch.poll_stash", side_effect=fake_poll):
        result = runner.invoke(watch_cmd, ["start", "myenv", "--interval", "0"])

    assert "change #1" in result.output
    assert "~ A" in result.output
    assert "+ B=added" in result.output


def test_start_quiet_only_prints_name(runner):
    def fake_poll(name, interval, max_polls, on_change):
        on_change(name, {"A": "1"}, {"A": "2"})

    with patch("stashpoint.cli_watch.poll_stash", side_effect=fake_poll):
        result = runner.invoke(watch_cmd, ["start", "myenv", "--quiet", "--interval", "0"])

    assert result.output.strip() == "myenv"


def test_start_keyboard_interrupt_exits_cleanly(runner):
    with patch("stashpoint.cli_watch.poll_stash", side_effect=KeyboardInterrupt):
        result = runner.invoke(watch_cmd, ["start", "myenv"])

    assert "Watch stopped" in result.output
    assert result.exit_code == 0


def test_start_removed_key_shown(runner):
    def fake_poll(name, interval, max_polls, on_change):
        on_change(name, {"GONE": "val"}, {})

    with patch("stashpoint.cli_watch.poll_stash", side_effect=fake_poll):
        result = runner.invoke(watch_cmd, ["start", "env", "--interval", "0"])

    assert "- GONE" in result.output
