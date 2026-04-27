"""Tests for stashpoint.cli_priority."""

import pytest
from click.testing import CliRunner

from stashpoint.cli_priority import priority_cmd
from stashpoint.priority import DEFAULT_PRIORITY


@pytest.fixture()
def runner():
    return CliRunner()


def test_set_command_success(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_priority.set_priority", lambda n, l: l)
    result = runner.invoke(priority_cmd, ["set", "myenv", "7"])
    assert result.exit_code == 0
    assert "7" in result.output
    assert "myenv" in result.output


def test_set_command_stash_not_found(runner, monkeypatch):
    from stashpoint.priority import StashNotFoundError

    monkeypatch.setattr(
        "stashpoint.cli_priority.set_priority",
        lambda n, l: (_ for _ in ()).throw(StashNotFoundError("not found")),
    )
    result = runner.invoke(priority_cmd, ["set", "ghost", "5"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_set_command_invalid_priority(runner, monkeypatch):
    from stashpoint.priority import InvalidPriorityError

    monkeypatch.setattr(
        "stashpoint.cli_priority.set_priority",
        lambda n, l: (_ for _ in ()).throw(InvalidPriorityError("bad level")),
    )
    result = runner.invoke(priority_cmd, ["set", "myenv", "99"])
    assert result.exit_code != 0
    assert "bad level" in result.output


def test_get_command_shows_default(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_priority.get_priority", lambda n: DEFAULT_PRIORITY)
    result = runner.invoke(priority_cmd, ["get", "myenv"])
    assert result.exit_code == 0
    assert "default" in result.output
    assert str(DEFAULT_PRIORITY) in result.output


def test_get_command_shows_custom(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_priority.get_priority", lambda n: 9)
    result = runner.invoke(priority_cmd, ["get", "myenv"])
    assert result.exit_code == 0
    assert "9" in result.output
    assert "default" not in result.output


def test_remove_command_removed(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_priority.remove_priority", lambda n: True)
    result = runner.invoke(priority_cmd, ["remove", "myenv"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_command_not_set(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_priority.remove_priority", lambda n: False)
    result = runner.invoke(priority_cmd, ["remove", "myenv"])
    assert result.exit_code == 0
    assert "No explicit priority" in result.output


def test_list_command_shows_explicit(runner, monkeypatch):
    monkeypatch.setattr(
        "stashpoint.cli_priority.load_stashes",
        lambda: {"alpha": {}, "beta": {}},
    )
    monkeypatch.setattr(
        "stashpoint.cli_priority.load_priorities",
        lambda: {"alpha": 8},
    )
    monkeypatch.setattr(
        "stashpoint.cli_priority.rank_by_priority",
        lambda names: sorted(names, reverse=True),
    )
    result = runner.invoke(priority_cmd, ["list"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" not in result.output
