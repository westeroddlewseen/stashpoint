"""Tests for stashpoint.merge and cli_merge."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from stashpoint.merge import merge_stashes, get_conflicts, StashNotFoundError
from stashpoint.cli_merge import merge_cmd


STASHES = {
    "base": {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"},
    "dev": {"HOST": "devhost", "DEBUG": "true", "LOG_LEVEL": "debug"},
}


# --- Unit tests for merge logic ---

def test_merge_no_conflicts():
    stashes = {"a": {"FOO": "1"}, "b": {"BAR": "2"}}
    result = merge_stashes(stashes, "a", "b")
    assert result == {"BAR": "2", "FOO": "1"}


def test_merge_keeps_target_on_conflict_without_overwrite():
    result = merge_stashes(STASHES, "dev", "base", overwrite=False)
    assert result["HOST"] == "localhost"  # target wins
    assert result["LOG_LEVEL"] == "debug"  # new key added


def test_merge_overwrites_on_conflict():
    result = merge_stashes(STASHES, "dev", "base", overwrite=True)
    assert result["HOST"] == "devhost"  # source wins
    assert result["DEBUG"] == "true"


def test_merge_source_not_found():
    with pytest.raises(StashNotFoundError, match="missing"):
        merge_stashes(STASHES, "missing", "base")


def test_merge_target_not_found():
    with pytest.raises(StashNotFoundError, match="missing"):
        merge_stashes(STASHES, "base", "missing")


def test_get_conflicts():
    conflicts = get_conflicts(STASHES, "dev", "base")
    assert "HOST" in conflicts
    assert conflicts["HOST"] == ("localhost", "devhost")
    assert "LOG_LEVEL" not in conflicts  # only in source, not a conflict


def test_get_conflicts_missing_stash_returns_empty():
    assert get_conflicts(STASHES, "nope", "base") == {}


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_merge_success(runner):
    stashes = {"a": {"X": "1"}, "b": {"Y": "2"}}
    with patch("stashpoint.cli_merge.load_stashes", return_value=stashes), \
         patch("stashpoint.cli_merge.save_stashes") as mock_save:
        result = runner.invoke(merge_cmd, ["a", "b"])
        assert result.exit_code == 0
        assert "Merged" in result.output
        mock_save.assert_called_once()


def test_cli_merge_conflict_aborts(runner):
    with patch("stashpoint.cli_merge.load_stashes", return_value=STASHES), \
         patch("stashpoint.cli_merge.save_stashes") as mock_save:
        result = runner.invoke(merge_cmd, ["dev", "base"])
        assert result.exit_code != 0
        assert "Conflicts" in result.output
        mock_save.assert_not_called()


def test_cli_merge_dry_run(runner):
    stashes = {"a": {"X": "1"}, "b": {"Y": "2"}}
    with patch("stashpoint.cli_merge.load_stashes", return_value=stashes), \
         patch("stashpoint.cli_merge.save_stashes") as mock_save:
        result = runner.invoke(merge_cmd, ["a", "b", "--dry-run"])
        assert result.exit_code == 0
        assert "dry-run" in result.output
        mock_save.assert_not_called()


def test_cli_merge_not_found(runner):
    with patch("stashpoint.cli_merge.load_stashes", return_value=STASHES):
        result = runner.invoke(merge_cmd, ["ghost", "base"])
        assert result.exit_code != 0
