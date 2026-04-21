"""Tests for stashpoint.cli_profile commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from stashpoint.cli_profile import profile_cmd
from stashpoint.profile import ProfileAlreadyExistsError, ProfileNotFoundError


@pytest.fixture
def runner():
    return CliRunner()


def test_create_profile(runner):
    with patch("stashpoint.cli_profile.create_profile") as mock_create:
        result = runner.invoke(profile_cmd, ["create", "dev", "base", "secrets"])
        mock_create.assert_called_once_with("dev", ["base", "secrets"], overwrite=False)
        assert "created" in result.output


def test_create_profile_already_exists(runner):
    with patch("stashpoint.cli_profile.create_profile", side_effect=ProfileAlreadyExistsError("exists")):
        result = runner.invoke(profile_cmd, ["create", "dev"])
        assert result.exit_code == 1
        assert "exists" in result.output


def test_delete_profile(runner):
    with patch("stashpoint.cli_profile.delete_profile") as mock_del:
        result = runner.invoke(profile_cmd, ["delete", "dev"])
        mock_del.assert_called_once_with("dev")
        assert "deleted" in result.output


def test_delete_profile_not_found(runner):
    with patch("stashpoint.cli_profile.delete_profile", side_effect=ProfileNotFoundError("nope")):
        result = runner.invoke(profile_cmd, ["delete", "ghost"])
        assert result.exit_code == 1


def test_show_profile(runner):
    with patch("stashpoint.cli_profile.get_profile", return_value=["base", "secrets"]):
        result = runner.invoke(profile_cmd, ["show", "dev"])
        assert "base" in result.output
        assert "secrets" in result.output


def test_show_profile_empty(runner):
    with patch("stashpoint.cli_profile.get_profile", return_value=[]):
        result = runner.invoke(profile_cmd, ["show", "dev"])
        assert "empty" in result.output


def test_show_profile_not_found(runner):
    with patch("stashpoint.cli_profile.get_profile", side_effect=ProfileNotFoundError("nope")):
        result = runner.invoke(profile_cmd, ["show", "ghost"])
        assert result.exit_code == 1


def test_list_profiles(runner):
    with patch("stashpoint.cli_profile.load_profiles", return_value={"dev": ["a", "b"], "prod": ["c"]}):
        result = runner.invoke(profile_cmd, ["list"])
        assert "dev" in result.output
        assert "prod" in result.output


def test_list_profiles_empty(runner):
    with patch("stashpoint.cli_profile.load_profiles", return_value={}):
        result = runner.invoke(profile_cmd, ["list"])
        assert "No profiles" in result.output


def test_add_stash_to_profile(runner):
    with patch("stashpoint.cli_profile.add_stash_to_profile") as mock_add:
        result = runner.invoke(profile_cmd, ["add", "dev", "extra"])
        mock_add.assert_called_once_with("dev", "extra")
        assert "Added" in result.output


def test_remove_stash_from_profile(runner):
    with patch("stashpoint.cli_profile.remove_stash_from_profile") as mock_rm:
        result = runner.invoke(profile_cmd, ["remove", "dev", "extra"])
        mock_rm.assert_called_once_with("dev", "extra")
        assert "Removed" in result.output
