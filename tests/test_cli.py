import pytest
from click.testing import CliRunner
from unittest.mock import patch
from stashpoint.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_save_command(runner):
    with patch("stashpoint.cli.save_stash") as mock_save:
        result = runner.invoke(cli, ["save", "myenv", "-v", "FOO=bar", "-v", "BAZ=qux"])
        assert result.exit_code == 0
        assert "myenv" in result.output
        assert "2 variable" in result.output
        mock_save.assert_called_once_with("myenv", {"FOO": "bar", "BAZ": "qux"})


def test_save_command_no_vars(runner):
    result = runner.invoke(cli, ["save", "myenv"])
    assert result.exit_code != 0
    assert "at least one variable" in result.output


def test_save_command_invalid_var_format(runner):
    result = runner.invoke(cli, ["save", "myenv", "-v", "BADFORMAT"])
    assert result.exit_code != 0


def test_load_command_bash(runner):
    with patch("stashpoint.cli.load_stash", return_value={"FOO": "bar"}):
        result = runner.invoke(cli, ["load", "myenv"])
        assert result.exit_code == 0
        assert "export FOO='bar'" in result.output


def test_load_command_fish(runner):
    with patch("stashpoint.cli.load_stash", return_value={"FOO": "bar"}):
        result = runner.invoke(cli, ["load", "myenv", "--shell", "fish"])
        assert result.exit_code == 0
        assert "set -x FOO 'bar';" in result.output


def test_load_command_json(runner):
    with patch("stashpoint.cli.load_stash", return_value={"FOO": "bar"}):
        result = runner.invoke(cli, ["load", "myenv", "--shell", "json"])
        assert result.exit_code == 0
        assert '"FOO": "bar"' in result.output


def test_load_command_not_found(runner):
    with patch("stashpoint.cli.load_stash", return_value=None):
        result = runner.invoke(cli, ["load", "ghost"])
        assert result.exit_code != 0
        assert "not found" in result.output


def test_list_command(runner):
    with patch("stashpoint.cli.list_stashes", return_value=["alpha", "beta"]):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "alpha" in result.output
        assert "beta" in result.output


def test_list_command_empty(runner):
    with patch("stashpoint.cli.list_stashes", return_value=[]):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "No stashes" in result.output


def test_delete_command(runner):
    with patch("stashpoint.cli.delete_stash", return_value=True):
        result = runner.invoke(cli, ["delete", "myenv"], input="y\n")
        assert result.exit_code == 0
        assert "deleted" in result.output


def test_delete_command_not_found(runner):
    with patch("stashpoint.cli.delete_stash", return_value=False):
        result = runner.invoke(cli, ["delete", "ghost"], input="y\n")
        assert result.exit_code != 0
        assert "not found" in result.output
