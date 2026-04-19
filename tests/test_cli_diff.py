"""Tests for the diff CLI command."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from stashpoint.cli_diff import diff_cmd


@pytest.fixture
def runner():
    return CliRunner()


def test_diff_no_differences(runner):
    stash = {"FOO": "bar"}
    with patch("stashpoint.cli_diff.load_stash", return_value=stash):
        result = runner.invoke(diff_cmd, ["alpha", "beta"])
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_diff_with_changes(runner):
    stash_a = {"FOO": "old", "ONLY_A": "x"}
    stash_b = {"FOO": "new", "ONLY_B": "y"}

    def mock_load(name):
        return stash_a if name == "alpha" else stash_b

    with patch("stashpoint.cli_diff.load_stash", side_effect=mock_load):
        result = runner.invoke(diff_cmd, ["alpha", "beta"])
    assert result.exit_code == 0
    assert "FOO" in result.output
    assert "ONLY_A" in result.output
    assert "ONLY_B" in result.output


def test_diff_stash_a_not_found(runner):
    with patch("stashpoint.cli_diff.load_stash", return_value=None):
        result = runner.invoke(diff_cmd, ["missing", "beta"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_diff_stash_b_not_found(runner):
    def mock_load(name):
        return {"A": "1"} if name == "alpha" else None

    with patch("stashpoint.cli_diff.load_stash", side_effect=mock_load):
        result = runner.invoke(diff_cmd, ["alpha", "missing"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()
