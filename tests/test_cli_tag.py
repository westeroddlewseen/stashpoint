import pytest
from click.testing import CliRunner
from unittest.mock import patch

from stashpoint.cli_tag import tag_cmd


@pytest.fixture
def runner():
    return CliRunner()


def test_add_tag(runner):
    with patch("stashpoint.cli_tag.add_tag") as mock_add:
        result = runner.invoke(tag_cmd, ["add", "myproject", "production"])
        assert result.exit_code == 0
        mock_add.assert_called_once_with("myproject", "production")
        assert "Tagged" in result.output


def test_remove_tag(runner):
    with patch("stashpoint.cli_tag.remove_tag") as mock_remove:
        result = runner.invoke(tag_cmd, ["remove", "myproject", "production"])
        assert result.exit_code == 0
        mock_remove.assert_called_once_with("myproject", "production")
        assert "Removed" in result.output


def test_list_tags(runner):
    with patch("stashpoint.cli_tag.get_tags", return_value=["aws", "production"]):
        result = runner.invoke(tag_cmd, ["list", "myproject"])
        assert result.exit_code == 0
        assert "aws" in result.output
        assert "production" in result.output


def test_list_tags_empty(runner):
    with patch("stashpoint.cli_tag.get_tags", return_value=[]):
        result = runner.invoke(tag_cmd, ["list", "myproject"])
        assert result.exit_code == 0
        assert "No tags" in result.output


def test_find_by_tag(runner):
    with patch("stashpoint.cli_tag.find_by_tag", return_value=["proj-a", "proj-b"]):
        result = runner.invoke(tag_cmd, ["find", "aws"])
        assert result.exit_code == 0
        assert "proj-a" in result.output
        assert "proj-b" in result.output


def test_find_by_tag_no_results(runner):
    with patch("stashpoint.cli_tag.find_by_tag", return_value=[]):
        result = runner.invoke(tag_cmd, ["find", "ghost"])
        assert result.exit_code == 0
        assert "No stashes found" in result.output
