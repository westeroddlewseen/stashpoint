"""Tests for stashpoint.cli_category."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from stashpoint.cli_category import category_cmd
from stashpoint.category import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    StashNotFoundError,
)


@pytest.fixture
def runner():
    return CliRunner()


def test_create_category_success(runner):
    with patch("stashpoint.cli_category.create_category") as mock_create:
        result = runner.invoke(category_cmd, ["create", "work"])
    assert result.exit_code == 0
    assert "created" in result.output
    mock_create.assert_called_once_with("work", overwrite=False)


def test_create_category_already_exists(runner):
    with patch("stashpoint.cli_category.create_category",
               side_effect=CategoryAlreadyExistsError("Category 'work' already exists.")):
        result = runner.invoke(category_cmd, ["create", "work"])
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_create_category_overwrite_flag(runner):
    with patch("stashpoint.cli_category.create_category") as mock_create:
        result = runner.invoke(category_cmd, ["create", "work", "--overwrite"])
    assert result.exit_code == 0
    mock_create.assert_called_once_with("work", overwrite=True)


def test_delete_category_success(runner):
    with patch("stashpoint.cli_category.delete_category") as mock_del:
        result = runner.invoke(category_cmd, ["delete", "work"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_category_not_found(runner):
    with patch("stashpoint.cli_category.delete_category",
               side_effect=CategoryNotFoundError("Category 'x' not found.")):
        result = runner.invoke(category_cmd, ["delete", "x"])
    assert result.exit_code == 1


def test_add_stash_to_category(runner):
    with patch("stashpoint.cli_category.add_to_category") as mock_add:
        result = runner.invoke(category_cmd, ["add", "work", "dev"])
    assert result.exit_code == 0
    assert "Added" in result.output
    mock_add.assert_called_once_with("work", "dev")


def test_add_stash_not_found(runner):
    with patch("stashpoint.cli_category.add_to_category",
               side_effect=StashNotFoundError("Stash 'ghost' not found.")):
        result = runner.invoke(category_cmd, ["add", "work", "ghost"])
    assert result.exit_code == 1


def test_list_categories_empty(runner):
    with patch("stashpoint.cli_category.load_categories", return_value={}):
        result = runner.invoke(category_cmd, ["list"])
    assert "No categories" in result.output


def test_list_categories_with_members(runner):
    data = {"work": ["dev", "prod"], "personal": []}
    with patch("stashpoint.cli_category.load_categories", return_value=data):
        result = runner.invoke(category_cmd, ["list"])
    assert "work" in result.output
    assert "dev" in result.output
    assert "(empty)" in result.output


def test_find_stash_categories(runner):
    with patch("stashpoint.cli_category.get_stash_categories", return_value=["alpha", "beta"]):
        result = runner.invoke(category_cmd, ["find", "dev"])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_find_stash_no_categories(runner):
    with patch("stashpoint.cli_category.get_stash_categories", return_value=[]):
        result = runner.invoke(category_cmd, ["find", "dev"])
    assert "not in any category" in result.output
