"""Tests for stashpoint.cli_favorite."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from stashpoint.cli_favorite import favorite_cmd
from stashpoint.favorite import StashNotFoundError, AlreadyFavoritedError


@pytest.fixture
def runner():
    return CliRunner()


def test_add_favorite_success(runner):
    with patch("stashpoint.cli_favorite.load_stashes", return_value={"dev": {}}), \
         patch("stashpoint.cli_favorite.add_favorite") as mock_add:
        result = runner.invoke(favorite_cmd, ["add", "dev"])
    assert result.exit_code == 0
    assert "Added 'dev' to favorites" in result.output


def test_add_favorite_stash_not_found(runner):
    with patch("stashpoint.cli_favorite.load_stashes", return_value={}), \
         patch("stashpoint.cli_favorite.add_favorite", side_effect=StashNotFoundError("not found")):
        result = runner.invoke(favorite_cmd, ["add", "ghost"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_add_favorite_already_favorited(runner):
    with patch("stashpoint.cli_favorite.load_stashes", return_value={"dev": {}}), \
         patch("stashpoint.cli_favorite.add_favorite", side_effect=AlreadyFavoritedError("already")):
        result = runner.invoke(favorite_cmd, ["add", "dev"])
    assert result.exit_code == 1
    assert "already" in result.output


def test_remove_favorite_success(runner):
    with patch("stashpoint.cli_favorite.remove_favorite", return_value=True):
        result = runner.invoke(favorite_cmd, ["remove", "dev"])
    assert result.exit_code == 0
    assert "Removed 'dev'" in result.output


def test_remove_favorite_not_found(runner):
    with patch("stashpoint.cli_favorite.remove_favorite", return_value=False):
        result = runner.invoke(favorite_cmd, ["remove", "dev"])
    assert result.exit_code == 1
    assert "not in favorites" in result.output


def test_list_favorites_empty(runner):
    with patch("stashpoint.cli_favorite.list_favorites", return_value=[]):
        result = runner.invoke(favorite_cmd, ["list"])
    assert result.exit_code == 0
    assert "No favorites" in result.output


def test_list_favorites_shows_names(runner):
    with patch("stashpoint.cli_favorite.list_favorites", return_value=["dev", "prod"]):
        result = runner.invoke(favorite_cmd, ["list"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_check_is_favorite(runner):
    with patch("stashpoint.cli_favorite.is_favorite", return_value=True):
        result = runner.invoke(favorite_cmd, ["check", "dev"])
    assert "is a favorite" in result.output


def test_check_not_favorite(runner):
    with patch("stashpoint.cli_favorite.is_favorite", return_value=False):
        result = runner.invoke(favorite_cmd, ["check", "dev"])
    assert "is not a favorite" in result.output
