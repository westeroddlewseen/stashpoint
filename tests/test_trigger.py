"""Tests for stashpoint.trigger and stashpoint.cli_trigger."""

import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch

from stashpoint.trigger import (
    register_trigger,
    unregister_trigger,
    get_trigger,
    list_triggers,
    TriggerNotFoundError,
)
from stashpoint.cli_trigger import trigger_cmd


@pytest.fixture()
def isolated_trigger(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def test_register_and_get_trigger(isolated_trigger, tmp_path):
    register_trigger(str(tmp_path), "myproject", "enter")
    result = get_trigger(str(tmp_path), "enter")
    assert result == "myproject"


def test_get_trigger_missing_returns_none(isolated_trigger, tmp_path):
    assert get_trigger(str(tmp_path), "enter") is None


def test_register_both_events(isolated_trigger, tmp_path):
    register_trigger(str(tmp_path), "on-enter", "enter")
    register_trigger(str(tmp_path), "on-leave", "leave")
    assert get_trigger(str(tmp_path), "enter") == "on-enter"
    assert get_trigger(str(tmp_path), "leave") == "on-leave"


def test_register_invalid_event_raises(isolated_trigger, tmp_path):
    with pytest.raises(ValueError, match="event must be"):
        register_trigger(str(tmp_path), "myproject", "hover")


def test_unregister_specific_event(isolated_trigger, tmp_path):
    register_trigger(str(tmp_path), "on-enter", "enter")
    register_trigger(str(tmp_path), "on-leave", "leave")
    unregister_trigger(str(tmp_path), "enter")
    assert get_trigger(str(tmp_path), "enter") is None
    assert get_trigger(str(tmp_path), "leave") == "on-leave"


def test_unregister_all_events(isolated_trigger, tmp_path):
    register_trigger(str(tmp_path), "myproject", "enter")
    unregister_trigger(str(tmp_path), None)
    assert get_trigger(str(tmp_path), "enter") is None


def test_unregister_not_found_raises(isolated_trigger, tmp_path):
    with pytest.raises(TriggerNotFoundError):
        unregister_trigger(str(tmp_path))


def test_list_triggers_empty(isolated_trigger):
    assert list_triggers() == []


def test_list_triggers_returns_sorted(isolated_trigger, tmp_path):
    dir_a = str(tmp_path / "aaa")
    dir_b = str(tmp_path / "bbb")
    register_trigger(dir_b, "stash-b", "enter")
    register_trigger(dir_a, "stash-a", "enter")
    entries = list_triggers()
    assert entries[0]["directory"] < entries[1]["directory"]


# --- CLI tests ---

def test_cli_add_trigger(isolated_trigger, runner, tmp_path):
    result = runner.invoke(trigger_cmd, ["add", str(tmp_path), "myproject"])
    assert result.exit_code == 0
    assert "enter" in result.output
    assert "myproject" in result.output


def test_cli_remove_trigger(isolated_trigger, runner, tmp_path):
    register_trigger(str(tmp_path), "myproject", "enter")
    result = runner.invoke(trigger_cmd, ["remove", str(tmp_path)])
    assert result.exit_code == 0


def test_cli_remove_trigger_not_found(isolated_trigger, runner, tmp_path):
    result = runner.invoke(trigger_cmd, ["remove", str(tmp_path)])
    assert result.exit_code == 1


def test_cli_list_no_triggers(isolated_trigger, runner):
    result = runner.invoke(trigger_cmd, ["list"])
    assert "No triggers" in result.output


def test_cli_check_returns_stash(isolated_trigger, runner, tmp_path):
    register_trigger(str(tmp_path), "myproject", "enter")
    result = runner.invoke(trigger_cmd, ["check", str(tmp_path)])
    assert result.exit_code == 0
    assert "myproject" in result.output


def test_cli_check_no_trigger_exits_1(isolated_trigger, runner, tmp_path):
    result = runner.invoke(trigger_cmd, ["check", str(tmp_path)])
    assert result.exit_code == 1
