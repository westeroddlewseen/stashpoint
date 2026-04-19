"""Tests for stashpoint.cli_history commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from stashpoint.cli_history import history_cmd


@pytest.fixture
def runner():
    return CliRunner()


SAMPLE_HISTORY = [
    {"action": "save", "stash": "proj", "timestamp": "2024-01-01T10:00:00", "variables": {"A": "1"}},
    {"action": "load", "stash": "proj", "timestamp": "2024-01-01T11:00:00", "variables": {"A": "1"}},
    {"action": "save", "stash": "other", "timestamp": "2024-01-02T09:00:00", "variables": {}},
]


def test_list_no_history(runner):
    with patch("stashpoint.cli_history.load_history", return_value=[]):
        result = runner.invoke(history_cmd, ["list"])
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_list_all_history(runner):
    with patch("stashpoint.cli_history.load_history", return_value=SAMPLE_HISTORY):
        result = runner.invoke(history_cmd, ["list"])
    assert result.exit_code == 0
    assert "proj" in result.output
    assert "other" in result.output


def test_list_filtered_by_stash(runner):
    filtered = [e for e in SAMPLE_HISTORY if e["stash"] == "proj"]
    with patch("stashpoint.cli_history.get_stash_history", return_value=filtered):
        result = runner.invoke(history_cmd, ["list", "--stash", "proj"])
    assert result.exit_code == 0
    assert "proj" in result.output
    assert "other" not in result.output


def test_list_limit(runner):
    with patch("stashpoint.cli_history.load_history", return_value=SAMPLE_HISTORY):
        result = runner.invoke(history_cmd, ["list", "--limit", "1"])
    assert result.exit_code == 0
    assert result.output.count("\n") == 1


def test_clear_history(runner):
    with patch("stashpoint.cli_history.clear_history") as mock_clear:
        result = runner.invoke(history_cmd, ["clear"], input="y\n")
    assert result.exit_code == 0
    mock_clear.assert_called_once()
    assert "cleared" in result.output


def test_clear_history_aborted(runner):
    with patch("stashpoint.cli_history.clear_history") as mock_clear:
        result = runner.invoke(history_cmd, ["clear"], input="n\n")
    mock_clear.assert_not_called()
