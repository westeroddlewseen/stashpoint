"""Tests for stashpoint.pin and stashpoint.cli_pin."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from stashpoint.pin import pin_stash, unpin_stash, is_pinned, list_pinned, load_pins, save_pins
from stashpoint.cli_pin import pin_cmd


@pytest.fixture
def mock_pins(tmp_path, monkeypatch):
    pin_file = tmp_path / "pins.json"
    monkeypatch.setattr("stashpoint.pin.get_pin_path", lambda: pin_file)
    return pin_file


@pytest.fixture
def runner():
    return CliRunner()


def test_is_pinned_false_by_default(mock_pins):
    assert is_pinned("myproject") is False


def test_pin_stash(mock_pins):
    pin_stash("myproject")
    assert is_pinned("myproject") is True


def test_pin_stash_idempotent(mock_pins):
    pin_stash("myproject")
    pin_stash("myproject")
    assert load_pins().count("myproject") == 1


def test_unpin_stash(mock_pins):
    pin_stash("myproject")
    unpin_stash("myproject")
    assert is_pinned("myproject") is False


def test_unpin_stash_idempotent(mock_pins):
    unpin_stash("myproject")  # should not raise
    assert is_pinned("myproject") is False


def test_list_pinned_sorted(mock_pins):
    pin_stash("zebra")
    pin_stash("alpha")
    pin_stash("middle")
    assert list_pinned() == ["alpha", "middle", "zebra"]


def test_cli_add_pin(mock_pins, runner):
    result = runner.invoke(pin_cmd, ["add", "myproject"])
    assert result.exit_code == 0
    assert "pinned" in result.output
    assert is_pinned("myproject")


def test_cli_add_pin_already_pinned(mock_pins, runner):
    pin_stash("myproject")
    result = runner.invoke(pin_cmd, ["add", "myproject"])
    assert result.exit_code == 0
    assert "already pinned" in result.output


def test_cli_remove_pin(mock_pins, runner):
    pin_stash("myproject")
    result = runner.invoke(pin_cmd, ["remove", "myproject"])
    assert result.exit_code == 0
    assert "unpinned" in result.output
    assert not is_pinned("myproject")


def test_cli_remove_pin_not_pinned(mock_pins, runner):
    result = runner.invoke(pin_cmd, ["remove", "myproject"])
    assert result.exit_code == 0
    assert "not pinned" in result.output


def test_cli_list_empty(mock_pins, runner):
    result = runner.invoke(pin_cmd, ["list"])
    assert result.exit_code == 0
    assert "No pinned" in result.output


def test_cli_list_with_pins(mock_pins, runner):
    pin_stash("alpha")
    pin_stash("beta")
    result = runner.invoke(pin_cmd, ["list"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_cli_check_pinned(mock_pins, runner):
    pin_stash("myproject")
    result = runner.invoke(pin_cmd, ["check", "myproject"])
    assert result.exit_code == 0
    assert "is pinned" in result.output


def test_cli_check_not_pinned(mock_pins, runner):
    result = runner.invoke(pin_cmd, ["check", "myproject"])
    assert result.exit_code == 0
    assert "is not pinned" in result.output
