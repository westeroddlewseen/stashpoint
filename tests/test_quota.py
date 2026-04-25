"""Tests for stashpoint.quota."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from stashpoint.quota import (
    QuotaExceededError,
    set_quota,
    clear_quota,
    load_quota,
    check_stash_count,
    check_var_count,
    get_quota_status,
)
from stashpoint.cli_quota import quota_cmd


@pytest.fixture(autouse=True)
def isolated_quota(tmp_path, monkeypatch):
    quota_file = tmp_path / "quota.json"
    monkeypatch.setattr("stashpoint.quota.get_quota_path", lambda: quota_file)
    monkeypatch.setattr("stashpoint.quota.get_stash_path", lambda: tmp_path / "stashes.json")
    yield quota_file


def test_load_quota_empty_returns_empty_dict():
    assert load_quota() == {}


def test_set_quota_max_stashes():
    result = set_quota(max_stashes=10)
    assert result["max_stashes"] == 10


def test_set_quota_max_vars():
    result = set_quota(max_vars_per_stash=20)
    assert result["max_vars_per_stash"] == 20


def test_set_quota_invalid_max_stashes_raises():
    with pytest.raises(ValueError):
        set_quota(max_stashes=0)


def test_set_quota_invalid_max_vars_raises():
    with pytest.raises(ValueError):
        set_quota(max_vars_per_stash=-1)


def test_clear_quota_removes_limits():
    set_quota(max_stashes=5, max_vars_per_stash=10)
    clear_quota()
    assert load_quota() == {}


def test_check_stash_count_no_limit_passes():
    with patch("stashpoint.quota.load_stashes", return_value={"a": {}, "b": {}}):
        check_stash_count()  # should not raise


def test_check_stash_count_under_limit_passes():
    set_quota(max_stashes=5)
    with patch("stashpoint.quota.load_stashes", return_value={"a": {}, "b": {}}):
        check_stash_count()  # should not raise


def test_check_stash_count_at_limit_raises():
    set_quota(max_stashes=2)
    with patch("stashpoint.quota.load_stashes", return_value={"a": {}, "b": {}}):
        with pytest.raises(QuotaExceededError, match="quota exceeded"):
            check_stash_count()


def test_check_var_count_no_limit_passes():
    check_var_count({"A": "1", "B": "2"})


def test_check_var_count_under_limit_passes():
    set_quota(max_vars_per_stash=5)
    check_var_count({"A": "1", "B": "2"})


def test_check_var_count_exceeds_limit_raises():
    set_quota(max_vars_per_stash=2)
    with pytest.raises(QuotaExceededError, match="Variable quota exceeded"):
        check_var_count({"A": "1", "B": "2", "C": "3"})


def test_get_quota_status_returns_current_count():
    set_quota(max_stashes=10, max_vars_per_stash=50)
    with patch("stashpoint.quota.load_stashes", return_value={"x": {}, "y": {}}):
        status = get_quota_status()
    assert status["max_stashes"] == 10
    assert status["max_vars_per_stash"] == 50
    assert status["current_stashes"] == 2


# CLI tests

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_set_max_stashes(runner):
    with patch("stashpoint.cli_quota.set_quota", return_value={"max_stashes": 5}) as mock:
        result = runner.invoke(quota_cmd, ["set", "--max-stashes", "5"])
    assert result.exit_code == 0
    assert "Max stashes set to 5" in result.output


def test_cli_set_no_options_errors(runner):
    result = runner.invoke(quota_cmd, ["set"])
    assert result.exit_code != 0


def test_cli_clear(runner):
    with patch("stashpoint.cli_quota.clear_quota") as mock:
        result = runner.invoke(quota_cmd, ["clear"])
    assert result.exit_code == 0
    assert "cleared" in result.output
    mock.assert_called_once()


def test_cli_status(runner):
    status = {"max_stashes": 10, "current_stashes": 3, "max_vars_per_stash": None}
    with patch("stashpoint.cli_quota.get_quota_status", return_value=status):
        result = runner.invoke(quota_cmd, ["status"])
    assert result.exit_code == 0
    assert "3 / 10" in result.output
    assert "unlimited" in result.output
