"""Tests for stashpoint.cli_health."""

import pytest
from click.testing import CliRunner
from stashpoint.cli_health import health_cmd
from stashpoint.health import HealthReport, HealthIssue, StashNotFoundError


@pytest.fixture
def runner():
    return CliRunner()


def _ok_report(name="dev"):
    return HealthReport(name=name, healthy=True, issues=[])


def _bad_report(name="broken"):
    return HealthReport(
        name=name,
        healthy=False,
        issues=[HealthIssue(severity="error", message="Stash has expired.")],
    )


def test_check_command_healthy(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_health.check_stash_health", lambda n: _ok_report(n))
    result = runner.invoke(health_cmd, ["check", "dev"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_check_command_unhealthy_exits_1(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_health.check_stash_health", lambda n: _bad_report(n))
    result = runner.invoke(health_cmd, ["check", "broken"])
    assert result.exit_code == 1
    assert "UNHEALTHY" in result.output


def test_check_command_not_found(runner, monkeypatch):
    def _raise(name):
        raise StashNotFoundError(f"Stash '{name}' not found.")
    monkeypatch.setattr("stashpoint.cli_health.check_stash_health", _raise)
    result = runner.invoke(health_cmd, ["check", "ghost"])
    assert result.exit_code == 1


def test_check_all_flag(runner, monkeypatch):
    monkeypatch.setattr(
        "stashpoint.cli_health.check_all_health",
        lambda: [_ok_report("a"), _ok_report("b")],
    )
    result = runner.invoke(health_cmd, ["check", "--all"])
    assert result.exit_code == 0
    assert "a" in result.output
    assert "b" in result.output


def test_check_all_errors_only_hides_healthy(runner, monkeypatch):
    monkeypatch.setattr(
        "stashpoint.cli_health.check_all_health",
        lambda: [_ok_report("good"), _bad_report("bad")],
    )
    result = runner.invoke(health_cmd, ["check", "--all", "--errors-only"])
    assert "good" not in result.output
    assert "bad" in result.output


def test_check_no_args_shows_usage_error(runner):
    result = runner.invoke(health_cmd, ["check"])
    assert result.exit_code != 0


def test_summary_command(runner, monkeypatch):
    monkeypatch.setattr(
        "stashpoint.cli_health.check_all_health",
        lambda: [_ok_report("a"), _bad_report("b")],
    )
    result = runner.invoke(health_cmd, ["summary"])
    assert "1/2" in result.output


def test_summary_no_stashes(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_health.check_all_health", lambda: [])
    result = runner.invoke(health_cmd, ["summary"])
    assert "No stashes" in result.output
