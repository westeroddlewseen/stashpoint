"""Tests for stashpoint export functionality."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from stashpoint.export import export_bash, export_fish, export_powershell, export_dotenv, export_variables
from stashpoint.cli_export import export_cmd


SAMPLE_VARS = {"API_KEY": "abc123", "DEBUG": "true", "DB_URL": 'postgres://user:"pass"@host/db'}


def test_export_bash():
    result = export_bash({"FOO": "bar", "BAZ": "qux"})
    assert 'export FOO="bar"' in result
    assert 'export BAZ="qux"' in result


def test_export_bash_escapes_quotes():
    result = export_bash({"MSG": 'say "hello"'})
    assert 'export MSG="say \\"hello\\""' in result


def test_export_fish():
    result = export_fish({"FOO": "bar"})
    assert 'set -x FOO "bar"' in result


def test_export_powershell():
    result = export_powershell({"FOO": "bar"})
    assert '$env:FOO = "bar"' in result


def test_export_dotenv():
    result = export_dotenv({"FOO": "bar"})
    assert 'FOO="bar"' in result


def test_export_variables_bash():
    result = export_variables({"X": "1"}, "bash")
    assert 'export X="1"' in result


def test_export_variables_zsh():
    result = export_variables({"X": "1"}, "zsh")
    assert 'export X="1"' in result


def test_export_variables_unsupported():
    with pytest.raises(ValueError, match="Unsupported shell format"):
        export_variables({"X": "1"}, "csh")


@pytest.fixture
def runner():
    return CliRunner()


def test_export_cmd_stdout(runner, tmp_path):
    with patch("stashpoint.cli_export.load_stash", return_value={"FOO": "bar"}):
        result = runner.invoke(export_cmd, ["mystash", "--shell", "bash"])
    assert result.exit_code == 0
    assert 'export FOO="bar"' in result.output


def test_export_cmd_to_file(runner, tmp_path):
    out_file = tmp_path / "env.sh"
    with patch("stashpoint.cli_export.load_stash", return_value={"FOO": "bar"}):
        result = runner.invoke(export_cmd, ["mystash", "--shell", "bash", "--output", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    assert 'export FOO="bar"' in out_file.read_text()


def test_export_cmd_not_found(runner):
    from stashpoint.storage import StashNotFoundError
    with patch("stashpoint.cli_export.load_stash", side_effect=StashNotFoundError("missing")):
        result = runner.invoke(export_cmd, ["missing"])
    assert result.exit_code != 0
    assert "not found" in result.output + (result.stderr if result.stderr_bytes else "")
