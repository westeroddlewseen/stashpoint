"""Tests for stashpoint.health."""

import pytest
from unittest.mock import patch

from stashpoint.health import (
    check_stash_health,
    check_all_health,
    format_health_report,
    HealthReport,
    HealthIssue,
    StashNotFoundError,
)


STASHES = {
    "dev": {"DB_HOST": "localhost", "PORT": "5432"},
    "empty": {},
    "bad": {"KEY": ""},
}


@pytest.fixture
def mock_deps(monkeypatch):
    monkeypatch.setattr("stashpoint.health.load_stashes", lambda: dict(STASHES))
    monkeypatch.setattr("stashpoint.health.load_expiry", lambda: {})
    monkeypatch.setattr("stashpoint.health.validate_stash", lambda v: None)


def test_stash_not_found_raises(mock_deps):
    with pytest.raises(StashNotFoundError):
        check_stash_health("nonexistent")


def test_healthy_stash_returns_healthy(mock_deps):
    report = check_stash_health("dev")
    assert report.healthy is True
    assert report.name == "dev"


def test_empty_stash_returns_warning(mock_deps):
    report = check_stash_health("empty")
    assert any(i.severity == "warning" for i in report.issues)
    assert report.healthy is True  # warnings don't make it unhealthy


def test_empty_value_returns_warning(mock_deps):
    report = check_stash_health("bad")
    messages = [i.message for i in report.issues]
    assert any("KEY" in m for m in messages)


def test_expired_stash_is_unhealthy(monkeypatch):
    monkeypatch.setattr("stashpoint.health.load_stashes", lambda: {"dev": {"X": "1"}})
    monkeypatch.setattr("stashpoint.health.load_expiry", lambda: {"dev": 1000.0})
    monkeypatch.setattr("stashpoint.health.validate_stash", lambda v: None)
    import time
    with patch("stashpoint.health.time") as mock_time:
        mock_time.time.return_value = 9999999.0
        report = check_stash_health("dev")
    assert not report.healthy
    assert any("expired" in i.message for i in report.issues)


def test_expiry_soon_warns(monkeypatch):
    import time as _time
    now = _time.time()
    monkeypatch.setattr("stashpoint.health.load_stashes", lambda: {"dev": {"X": "1"}})
    monkeypatch.setattr("stashpoint.health.load_expiry", lambda: {"dev": now + 3600})
    monkeypatch.setattr("stashpoint.health.validate_stash", lambda v: None)
    report = check_stash_health("dev")
    assert any("24 hours" in i.message for i in report.issues)


def test_check_all_returns_all_stashes(mock_deps):
    reports = check_all_health()
    names = {r.name for r in reports}
    assert names == {"dev", "empty", "bad"}


def test_format_health_report_ok(mock_deps):
    report = HealthReport(name="dev", healthy=True, issues=[])
    output = format_health_report(report)
    assert "[OK]" in output
    assert "dev" in output


def test_format_health_report_unhealthy():
    report = HealthReport(
        name="broken",
        healthy=False,
        issues=[HealthIssue(severity="error", message="Something failed.")],
    )
    output = format_health_report(report)
    assert "[UNHEALTHY]" in output
    assert "ERROR" in output
    assert "Something failed." in output


def test_errors_and_warnings_properties():
    report = HealthReport(
        name="x",
        healthy=False,
        issues=[
            HealthIssue(severity="error", message="e"),
            HealthIssue(severity="warning", message="w"),
        ],
    )
    assert len(report.errors) == 1
    assert len(report.warnings) == 1
