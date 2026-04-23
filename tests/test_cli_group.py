"""Tests for stashpoint.cli_group CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from stashpoint.cli_group import group_cmd
from stashpoint.group import GroupNotFoundError, GroupAlreadyExistsError


@pytest.fixture
def runner():
    return CliRunner()


def test_create_group_success(runner):
    with patch("stashpoint.cli_group.create_group") as mock_create:
        result = runner.invoke(group_cmd, ["create", "staging"])
    assert result.exit_code == 0
    assert "created" in result.output
    mock_create.assert_called_once_with("staging", overwrite=False)


def test_create_group_already_exists(runner):
    with patch("stashpoint.cli_group.create_group", side_effect=GroupAlreadyExistsError("Group 'staging' already exists.")):
        result = runner.invoke(group_cmd, ["create", "staging"])
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_create_group_overwrite_flag(runner):
    with patch("stashpoint.cli_group.create_group") as mock_create:
        result = runner.invoke(group_cmd, ["create", "staging", "--overwrite"])
    assert result.exit_code == 0
    mock_create.assert_called_once_with("staging", overwrite=True)


def test_delete_group_success(runner):
    with patch("stashpoint.cli_group.delete_group") as mock_del:
        result = runner.invoke(group_cmd, ["delete", "staging"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_group_not_found(runner):
    with patch("stashpoint.cli_group.delete_group", side_effect=GroupNotFoundError("Group 'staging' not found.")):
        result = runner.invoke(group_cmd, ["delete", "staging"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_add_stash_to_group(runner):
    with patch("stashpoint.cli_group.add_stash_to_group") as mock_add:
        result = runner.invoke(group_cmd, ["add", "mygroup", "stash-a"])
    assert result.exit_code == 0
    assert "Added" in result.output
    mock_add.assert_called_once_with("mygroup", "stash-a")


def test_remove_stash_from_group(runner):
    with patch("stashpoint.cli_group.remove_stash_from_group") as mock_rem:
        result = runner.invoke(group_cmd, ["remove", "mygroup", "stash-a"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_show_group_with_members(runner):
    with patch("stashpoint.cli_group.get_group_members", return_value=["stash-a", "stash-b"]):
        result = runner.invoke(group_cmd, ["show", "mygroup"])
    assert result.exit_code == 0
    assert "stash-a" in result.output
    assert "stash-b" in result.output


def test_show_group_empty(runner):
    with patch("stashpoint.cli_group.get_group_members", return_value=[]):
        result = runner.invoke(group_cmd, ["show", "mygroup"])
    assert result.exit_code == 0
    assert "empty" in result.output


def test_list_groups(runner):
    with patch("stashpoint.cli_group.list_groups", return_value=["alpha", "beta"]):
        result = runner.invoke(group_cmd, ["list"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_list_groups_empty(runner):
    with patch("stashpoint.cli_group.list_groups", return_value=[]):
        result = runner.invoke(group_cmd, ["list"])
    assert result.exit_code == 0
    assert "No groups" in result.output
