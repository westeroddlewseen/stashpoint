"""Tests for stashpoint.trust."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from stashpoint.trust import (
    TRUST_LEVELS,
    DEFAULT_TRUST,
    InvalidTrustLevelError,
    StashNotFoundError,
    set_trust,
    get_trust,
    remove_trust,
    list_trust,
)
from stashpoint.cli_trust import trust_cmd


@pytest.fixture
def mock_trust(tmp_path, monkeypatch):
    trust_file = tmp_path / "trust.json"
    monkeypatch.setattr("stashpoint.trust.get_trust_path", lambda: trust_file)
    return trust_file


def test_get_trust_default(mock_trust):
    assert get_trust("myproject") == DEFAULT_TRUST


def test_set_and_get_trust(mock_trust):
    set_trust("myproject", "high")
    assert get_trust("myproject") == "high"


def test_set_trust_stash_not_found(mock_trust):
    with pytest.raises(StashNotFoundError):
        set_trust("missing", "low", stashes={})


def test_set_trust_invalid_level(mock_trust):
    with pytest.raises(InvalidTrustLevelError):
        set_trust("myproject", "extreme")


def test_set_trust_all_valid_levels(mock_trust):
    for level in TRUST_LEVELS:
        set_trust("myproject", level)
        assert get_trust("myproject") == level


def test_remove_trust_returns_true(mock_trust):
    set_trust("myproject", "verified")
    result = remove_trust("myproject")
    assert result is True
    assert get_trust("myproject") == DEFAULT_TRUST


def test_remove_trust_not_set_returns_false(mock_trust):
    assert remove_trust("ghost") is False


def test_list_trust_empty(mock_trust):
    assert list_trust() == {}


def test_list_trust_returns_all(mock_trust):
    set_trust("a", "low")
    set_trust("b", "verified")
    result = list_trust()
    assert result == {"a": "low", "b": "verified"}


# CLI tests

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_set_success(runner, mock_trust):
    with patch("stashpoint.cli_trust.load_stashes", return_value={"proj": {}}):
        result = runner.invoke(trust_cmd, ["set", "proj", "high"])
    assert result.exit_code == 0
    assert "high" in result.output


def test_cli_set_stash_not_found(runner, mock_trust):
    with patch("stashpoint.cli_trust.load_stashes", return_value={}):
        result = runner.invoke(trust_cmd, ["set", "missing", "low"])
    assert result.exit_code == 1


def test_cli_get(runner, mock_trust):
    set_trust("proj", "verified")
    result = runner.invoke(trust_cmd, ["get", "proj"])
    assert "verified" in result.output


def test_cli_remove(runner, mock_trust):
    set_trust("proj", "low")
    result = runner.invoke(trust_cmd, ["remove", "proj"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_list_empty(runner, mock_trust):
    result = runner.invoke(trust_cmd, ["list"])
    assert "No trust levels" in result.output


def test_cli_list_shows_entries(runner, mock_trust):
    set_trust("alpha", "medium")
    result = runner.invoke(trust_cmd, ["list"])
    assert "alpha" in result.output
    assert "medium" in result.output
