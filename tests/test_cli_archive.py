"""Tests for stashpoint.cli_archive CLI commands."""

import json
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from stashpoint.cli_archive import archive_cmd
from stashpoint.archive import ARCHIVE_MANIFEST, STASHES_FILE


@pytest.fixture
def runner():
    return CliRunner()


@patch(
    "stashpoint.cli_archive.create_archive",
    return_value={"archived": ["prod", "dev"], "path": "/tmp/out.zip"},
)
def test_create_command_success(mock_create, runner):
    result = runner.invoke(archive_cmd, ["create", "prod", "dev", "-o", "/tmp/out.zip"])
    assert result.exit_code == 0
    assert "2 stash" in result.output
    assert "+ prod" in result.output
    assert "+ dev" in result.output


@patch(
    "stashpoint.cli_archive.create_archive",
    side_effect=__import__("stashpoint.archive", fromlist=["StashNotFoundError"]).StashNotFoundError("Stashes not found: staging"),
)
def test_create_command_missing_stash(mock_create, runner):
    result = runner.invoke(archive_cmd, ["create", "staging", "-o", "/tmp/out.zip"])
    assert result.exit_code != 0
    assert "staging" in result.output


@patch(
    "stashpoint.cli_archive.restore_archive",
    return_value={"restored": ["prod"], "skipped": []},
)
def test_restore_command_success(mock_restore, runner):
    result = runner.invoke(archive_cmd, ["restore", "/tmp/archive.zip"])
    assert result.exit_code == 0
    assert "+ prod" in result.output


@patch(
    "stashpoint.cli_archive.restore_archive",
    return_value={"restored": [], "skipped": ["prod"]},
)
def test_restore_command_shows_skipped(mock_restore, runner):
    result = runner.invoke(archive_cmd, ["restore", "/tmp/archive.zip"])
    assert result.exit_code == 0
    assert "~ prod" in result.output


@patch(
    "stashpoint.cli_archive.restore_archive",
    side_effect=__import__("stashpoint.archive", fromlist=["ArchiveError"]).ArchiveError("Not a valid stashpoint archive."),
)
def test_restore_command_invalid_archive(mock_restore, runner):
    result = runner.invoke(archive_cmd, ["restore", "/tmp/bad.zip"])
    assert result.exit_code != 0
    assert "valid stashpoint archive" in result.output


@patch(
    "stashpoint.cli_archive.restore_archive",
    return_value={"restored": [], "skipped": []},
)
def test_restore_command_empty_archive(mock_restore, runner):
    result = runner.invoke(archive_cmd, ["restore", "/tmp/empty.zip"])
    assert result.exit_code == 0
    assert "no stashes" in result.output
