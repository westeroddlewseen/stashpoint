"""Tests for stashpoint.cli_template."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from stashpoint.cli_template import template_cmd


@pytest.fixture
def runner():
    return CliRunner()


def test_list_templates(runner):
    result = runner.invoke(template_cmd, ["list"])
    assert result.exit_code == 0
    assert "python-dev" in result.output
    assert "docker" in result.output


def test_show_template(runner):
    result = runner.invoke(template_cmd, ["show", "python-dev"])
    assert result.exit_code == 0
    assert "PYTHONDONTWRITEBYTECODE" in result.output


def test_show_template_not_found(runner):
    result = runner.invoke(template_cmd, ["show", "bogus"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_apply_template_creates_stash(runner):
    with patch("stashpoint.cli_template.load_stash", return_value=None), \
         patch("stashpoint.cli_template.save_stash") as mock_save:
        result = runner.invoke(template_cmd, ["apply", "docker", "my-stash"])
        assert result.exit_code == 0
        assert "created" in result.output
        mock_save.assert_called_once()
        name, variables = mock_save.call_args[0]
        assert name == "my-stash"
        assert "DOCKER_BUILDKIT" in variables


def test_apply_template_with_overrides(runner):
    with patch("stashpoint.cli_template.load_stash", return_value=None), \
         patch("stashpoint.cli_template.save_stash") as mock_save:
        result = runner.invoke(
            template_cmd,
            ["apply", "django", "proj", "--set", "DEBUG=False"]
        )
        assert result.exit_code == 0
        _, variables = mock_save.call_args[0]
        assert variables["DEBUG"] == "False"


def test_apply_template_existing_no_overwrite(runner):
    with patch("stashpoint.cli_template.load_stash", return_value={"A": "1"}):
        result = runner.invoke(template_cmd, ["apply", "docker", "existing"])
        assert result.exit_code != 0
        assert "already exists" in result.output


def test_apply_template_existing_with_overwrite(runner):
    with patch("stashpoint.cli_template.load_stash", return_value={"A": "1"}), \
         patch("stashpoint.cli_template.save_stash") as mock_save:
        result = runner.invoke(
            template_cmd, ["apply", "docker", "existing", "--overwrite"]
        )
        assert result.exit_code == 0
        mock_save.assert_called_once()


def test_apply_template_invalid_override_format(runner):
    with patch("stashpoint.cli_template.load_stash", return_value=None):
        result = runner.invoke(
            template_cmd, ["apply", "docker", "s", "--set", "BADFORMAT"]
        )
        assert result.exit_code != 0
        assert "Invalid format" in result.output
