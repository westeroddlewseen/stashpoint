"""Tests for stashpoint.rollback."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from stashpoint.rollback import (
    list_rollback_points,
    rollback_stash,
    get_rollback_summary,
    StashNotFoundError,
    RollbackPointNotFoundError,
)
from stashpoint.cli_rollback import rollback_cmd


SAMPLE_HISTORY = [
    {"stash": "myenv", "action": "save", "timestamp": "2024-01-01T10:00:00",
     "snapshot": {"FOO": "bar", "BAZ": "qux"}},
    {"stash": "myenv", "action": "save", "timestamp": "2024-01-02T10:00:00",
     "snapshot": {"FOO": "newbar"}},
    {"stash": "other", "action": "save", "timestamp": "2024-01-01T09:00:00",
     "snapshot": {"X": "1"}},
    {"stash": "myenv", "action": "delete", "timestamp": "2024-01-03T10:00:00"},
]


@pytest.fixture
def mock_history():
    with patch("stashpoint.rollback.load_history", return_value=SAMPLE_HISTORY):
        yield


@pytest.fixture
def mock_stashes():
    with patch("stashpoint.rollback.load_stashes", return_value={"myenv": {"FOO": "newbar"}}):
        with patch("stashpoint.rollback.save_stash") as mock_save:
            yield mock_save


def test_list_rollback_points_filters_by_stash(mock_history):
    points = list_rollback_points("myenv")
    assert len(points) == 2
    assert all(p["stash"] == "myenv" for p in points)
    assert all(p["action"] == "save" for p in points)


def test_list_rollback_points_most_recent_first(mock_history):
    points = list_rollback_points("myenv")
    assert points[0]["timestamp"] == "2024-01-02T10:00:00"
    assert points[1]["timestamp"] == "2024-01-01T10:00:00"


def test_list_rollback_points_empty_for_unknown(mock_history):
    points = list_rollback_points("nonexistent")
    assert points == []


def test_rollback_stash_applies_snapshot(mock_history, mock_stashes):
    restored = rollback_stash("myenv", 0, overwrite=True)
    assert restored == {"FOO": "newbar"}
    mock_stashes.assert_called_once_with("myenv", {"FOO": "newbar"})


def test_rollback_stash_older_point(mock_history, mock_stashes):
    restored = rollback_stash("myenv", 1, overwrite=True)
    assert restored == {"FOO": "bar", "BAZ": "qux"}


def test_rollback_stash_index_out_of_range(mock_history, mock_stashes):
    with pytest.raises(RollbackPointNotFoundError):
        rollback_stash("myenv", 99, overwrite=True)


def test_rollback_stash_no_points(mock_stashes):
    with patch("stashpoint.rollback.load_history", return_value=[]):
        with pytest.raises(RollbackPointNotFoundError):
            rollback_stash("myenv", 0, overwrite=True)


def test_get_rollback_summary_lists_points(mock_history):
    summary = get_rollback_summary("myenv")
    assert "[0]" in summary
    assert "[1]" in summary
    assert "2024-01-02" in summary


def test_get_rollback_summary_no_points():
    with patch("stashpoint.rollback.load_history", return_value=[]):
        summary = get_rollback_summary("myenv")
        assert "No rollback points" in summary


# CLI tests

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_list_rollback_points(runner, mock_history):
    result = runner.invoke(rollback_cmd, ["list", "myenv"])
    assert result.exit_code == 0
    assert "[0]" in result.output


def test_cli_apply_rollback(runner, mock_history, mock_stashes):
    result = runner.invoke(rollback_cmd, ["apply", "myenv", "0"])
    assert result.exit_code == 0
    assert "Rolled back" in result.output


def test_cli_apply_rollback_bad_index(runner, mock_stashes):
    with patch("stashpoint.rollback.load_history", return_value=[]):
        result = runner.invoke(rollback_cmd, ["apply", "myenv", "5"])
        assert result.exit_code == 1
        assert "Error" in result.output
