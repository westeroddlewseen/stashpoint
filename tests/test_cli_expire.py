"""Tests for stashpoint.cli_expire."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from stashpoint.cli_expire import expire_cmd
from stashpoint.expire import StashNotFoundError


@pytest.fixture()
def runner():
    return CliRunner()


def test_set_command_success(runner):
    future_ts = time.time() + 3600
    with patch("stashpoint.cli_expire.set_expiry", return_value=future_ts):
        result = runner.invoke(expire_cmd, ["set", "myproject", "--ttl", "3600"])
    assert result.exit_code == 0
    assert "myproject" in result.output
    assert "expire" in result.output.lower()


def test_set_command_stash_not_found(runner):
    with patch("stashpoint.cli_expire.set_expiry", side_effect=StashNotFoundError("Stash 'x' not found.")):
        result = runner.invoke(expire_cmd, ["set", "x", "--ttl", "60"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_clear_command_removed(runner):
    with patch("stashpoint.cli_expire.clear_expiry", return_value=True):
        result = runner.invoke(expire_cmd, ["clear", "myproject"])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_clear_command_nothing_to_clear(runner):
    with patch("stashpoint.cli_expire.clear_expiry", return_value=False):
        result = runner.invoke(expire_cmd, ["clear", "myproject"])
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_status_no_expiry(runner):
    with patch("stashpoint.cli_expire.get_expiry", return_value=None):
        result = runner.invoke(expire_cmd, ["status", "myproject"])
    assert result.exit_code == 0
    assert "no expiry" in result.output.lower()


def test_status_active(runner):
    future_ts = time.time() + 9999
    with (
        patch("stashpoint.cli_expire.get_expiry", return_value=future_ts),
        patch("stashpoint.cli_expire.is_expired", return_value=False),
    ):
        result = runner.invoke(expire_cmd, ["status", "myproject"])
    assert result.exit_code == 0
    assert "active" in result.output


def test_status_expired(runner):
    past_ts = time.time() - 1
    with (
        patch("stashpoint.cli_expire.get_expiry", return_value=past_ts),
        patch("stashpoint.cli_expire.is_expired", return_value=True),
    ):
        result = runner.invoke(expire_cmd, ["status", "myproject"])
    assert result.exit_code == 0
    assert "EXPIRED" in result.output


def test_purge_with_results(runner):
    with patch("stashpoint.cli_expire.purge_expired", return_value=["old1", "old2"]):
        result = runner.invoke(expire_cmd, ["purge"])
    assert result.exit_code == 0
    assert "old1" in result.output
    assert "2 stash" in result.output


def test_purge_nothing_expired(runner):
    with patch("stashpoint.cli_expire.purge_expired", return_value=[]):
        result = runner.invoke(expire_cmd, ["purge"])
    assert result.exit_code == 0
    assert "No expired" in result.output
