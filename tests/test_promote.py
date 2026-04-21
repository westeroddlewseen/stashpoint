"""Tests for stashpoint.promote."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from stashpoint.promote import promote_stash, StashNotFoundError, UnsupportedShellError
from stashpoint.cli_promote import promote_cmd


SAMPLE = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}


@pytest.fixture()
def mock_load():
    with patch("stashpoint.promote.load_stash", return_value=SAMPLE) as m:
        yield m


def test_promote_bash_contains_export(mock_load):
    result = promote_stash("myproject", "bash")
    assert "export DB_HOST=" in result
    assert "export DB_PORT=" in result


def test_promote_fish_syntax(mock_load):
    result = promote_stash("myproject", "fish")
    assert "set -x DB_HOST" in result


def test_promote_dotenv_format(mock_load):
    result = promote_stash("myproject", "dotenv")
    assert "DB_HOST=localhost" in result


def test_promote_with_prefix(mock_load):
    result = promote_stash("myproject", "bash", prefix="APP_")
    assert "export APP_DB_HOST=" in result
    assert "DB_HOST" not in result.replace("APP_DB_HOST", "")


def test_promote_with_key_filter(mock_load):
    result = promote_stash("myproject", "bash", keys=["DB_HOST"])
    assert "DB_HOST" in result
    assert "DB_PORT" not in result
    assert "API_KEY" not in result


def test_promote_stash_not_found():
    with patch("stashpoint.promote.load_stash", return_value=None):
        with pytest.raises(StashNotFoundError, match="myproject"):
            promote_stash("myproject", "bash")


def test_promote_unsupported_shell(mock_load):
    with pytest.raises(UnsupportedShellError, match="zsh"):
        promote_stash("myproject", "zsh")


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_promote_env_bash(runner):
    with patch("stashpoint.cli_promote.promote_stash", return_value="export DB_HOST=localhost") as m:
        result = runner.invoke(promote_cmd, ["env", "myproject", "--shell", "bash"])
        assert result.exit_code == 0
        assert "export DB_HOST=localhost" in result.output
        m.assert_called_once_with("myproject", "bash", prefix="", keys=[])


def test_cli_promote_env_not_found(runner):
    with patch("stashpoint.cli_promote.promote_stash", side_effect=StashNotFoundError("missing")):
        result = runner.invoke(promote_cmd, ["env", "missing"])
        assert result.exit_code != 0
        assert "missing" in result.output


def test_cli_promote_env_with_prefix(runner):
    with patch("stashpoint.cli_promote.promote_stash", return_value="export APP_DB_HOST=localhost") as m:
        result = runner.invoke(promote_cmd, ["env", "myproject", "--prefix", "APP_"])
        assert result.exit_code == 0
        m.assert_called_once_with("myproject", "bash", prefix="APP_", keys=[])


def test_cli_promote_env_with_keys(runner):
    with patch("stashpoint.cli_promote.promote_stash", return_value="export DB_HOST=localhost") as m:
        result = runner.invoke(promote_cmd, ["env", "myproject", "--key", "DB_HOST"])
        assert result.exit_code == 0
        m.assert_called_once_with("myproject", "bash", prefix="", keys=["DB_HOST"])
