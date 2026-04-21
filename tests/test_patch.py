"""Tests for stashpoint.patch and stashpoint.cli_patch."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from stashpoint.patch import patch_stash, get_patch_summary, StashNotFoundError, InvalidPatchError
from stashpoint.cli_patch import patch_cmd


# ---------------------------------------------------------------------------
# Unit tests for patch_stash
# ---------------------------------------------------------------------------

SAMPLE_STASHES = {
    "myproject": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"}
}


def _mock_load(stashes=None):
    return patch("stashpoint.patch.load_stashes", return_value=stashes or dict(SAMPLE_STASHES))


def _mock_save():
    return patch("stashpoint.patch.save_stash")


def test_patch_updates_key():
    with _mock_load(), _mock_save() as mock_save:
        result = patch_stash("myproject", {"DB_HOST": "remotehost"})
    assert result["DB_HOST"] == "remotehost"
    mock_save.assert_called_once()


def test_patch_adds_new_key():
    with _mock_load(), _mock_save():
        result = patch_stash("myproject", {"NEW_VAR": "hello"})
    assert result["NEW_VAR"] == "hello"
    assert result["DB_HOST"] == "localhost"


def test_patch_removes_key():
    with _mock_load(), _mock_save():
        result = patch_stash("myproject", {}, remove_keys=["DEBUG"])
    assert "DEBUG" not in result
    assert "DB_HOST" in result


def test_patch_removes_missing_key_silently():
    with _mock_load(), _mock_save():
        result = patch_stash("myproject", {}, remove_keys=["NONEXISTENT"])
    assert result == SAMPLE_STASHES["myproject"]


def test_patch_stash_not_found():
    with _mock_load({}):
        with pytest.raises(StashNotFoundError):
            patch_stash("ghost", {"X": "1"})


def test_patch_empty_raises_invalid():
    with _mock_load():
        with pytest.raises(InvalidPatchError):
            patch_stash("myproject", {}, remove_keys=[])


# ---------------------------------------------------------------------------
# Unit tests for get_patch_summary
# ---------------------------------------------------------------------------

def test_summary_added():
    summary = get_patch_summary({"A": "1"}, {"A": "1", "B": "2"})
    assert summary["added"] == {"B": "2"}
    assert summary["modified"] == {}
    assert summary["removed"] == {}


def test_summary_removed():
    summary = get_patch_summary({"A": "1", "B": "2"}, {"A": "1"})
    assert summary["removed"] == {"B": "2"}


def test_summary_modified():
    summary = get_patch_summary({"A": "old"}, {"A": "new"})
    assert summary["modified"] == {"A": {"old": "old", "new": "new"}}


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_patch_apply(runner):
    with patch("stashpoint.cli_patch.load_stash", return_value={"A": "1"}), \
         patch("stashpoint.cli_patch.patch_stash", return_value={"A": "2"}) as mock_patch:
        result = runner.invoke(patch_cmd, ["apply", "myproject", "--set", "A=2"])
    assert result.exit_code == 0
    assert "patched successfully" in result.output


def test_cli_patch_apply_with_summary(runner):
    with patch("stashpoint.cli_patch.load_stash", return_value={"A": "1"}), \
         patch("stashpoint.cli_patch.patch_stash", return_value={"A": "2"}):
        result = runner.invoke(patch_cmd, ["apply", "myproject", "--set", "A=2", "--summary"])
    assert "~" in result.output


def test_cli_patch_invalid_format(runner):
    result = runner.invoke(patch_cmd, ["apply", "myproject", "--set", "BADFORMAT"])
    assert result.exit_code != 0 or "Invalid format" in result.output


def test_cli_patch_stash_not_found(runner):
    with patch("stashpoint.cli_patch.load_stash", return_value={}), \
         patch("stashpoint.cli_patch.patch_stash", side_effect=StashNotFoundError("ghost")):
        result = runner.invoke(patch_cmd, ["apply", "ghost", "--set", "X=1"])
    assert result.exit_code == 1
    assert "Error" in result.output
