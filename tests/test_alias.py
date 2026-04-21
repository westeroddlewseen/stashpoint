"""Tests for stashpoint.alias and stashpoint.cli_alias."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from stashpoint.alias import (
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    AliasNotFoundError,
    AliasAlreadyExistsError,
    AliasTargetNotFoundError,
)
from stashpoint.cli_alias import alias_cmd


@pytest.fixture
def mock_aliases(tmp_path, monkeypatch):
    alias_file = tmp_path / "aliases.json"
    monkeypatch.setattr("stashpoint.alias.get_alias_path", lambda: alias_file)
    return alias_file


@pytest.fixture
def mock_stashes():
    return {"prod": {"DB_HOST": "db.prod"}, "dev": {"DB_HOST": "localhost"}}


def test_add_alias(mock_aliases, mock_stashes):
    with patch("stashpoint.alias.load_stashes", return_value=mock_stashes):
        add_alias("p", "prod")
    assert list_aliases() == {"p": "prod"}


def test_add_alias_target_not_found(mock_aliases, mock_stashes):
    with patch("stashpoint.alias.load_stashes", return_value=mock_stashes):
        with pytest.raises(AliasTargetNotFoundError):
            add_alias("x", "nonexistent")


def test_add_alias_already_exists_no_overwrite(mock_aliases, mock_stashes):
    with patch("stashpoint.alias.load_stashes", return_value=mock_stashes):
        add_alias("p", "prod")
        with pytest.raises(AliasAlreadyExistsError):
            add_alias("p", "dev")


def test_add_alias_overwrite(mock_aliases, mock_stashes):
    with patch("stashpoint.alias.load_stashes", return_value=mock_stashes):
        add_alias("p", "prod")
        add_alias("p", "dev", overwrite=True)
    assert list_aliases()["p"] == "dev"


def test_remove_alias(mock_aliases, mock_stashes):
    with patch("stashpoint.alias.load_stashes", return_value=mock_stashes):
        add_alias("p", "prod")
    remove_alias("p")
    assert "p" not in list_aliases()


def test_remove_alias_not_found(mock_aliases):
    with pytest.raises(AliasNotFoundError):
        remove_alias("ghost")


def test_resolve_alias(mock_aliases, mock_stashes):
    with patch("stashpoint.alias.load_stashes", return_value=mock_stashes):
        add_alias("p", "prod")
    assert resolve_alias("p") == "prod"


def test_resolve_alias_not_found(mock_aliases):
    with pytest.raises(AliasNotFoundError):
        resolve_alias("missing")


# CLI tests

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_add_alias(runner, mock_aliases, mock_stashes):
    with patch("stashpoint.alias.load_stashes", return_value=mock_stashes):
        result = runner.invoke(alias_cmd, ["add", "p", "prod"])
    assert result.exit_code == 0
    assert "created" in result.output


def test_cli_list_aliases(runner, mock_aliases, mock_stashes):
    with patch("stashpoint.alias.load_stashes", return_value=mock_stashes):
        runner.invoke(alias_cmd, ["add", "p", "prod"])
    result = runner.invoke(alias_cmd, ["list"])
    assert "p -> prod" in result.output


def test_cli_list_no_aliases(runner, mock_aliases):
    result = runner.invoke(alias_cmd, ["list"])
    assert "No aliases" in result.output


def test_cli_resolve(runner, mock_aliases, mock_stashes):
    with patch("stashpoint.alias.load_stashes", return_value=mock_stashes):
        runner.invoke(alias_cmd, ["add", "p", "prod"])
    result = runner.invoke(alias_cmd, ["resolve", "p"])
    assert "prod" in result.output


def test_cli_remove_alias(runner, mock_aliases, mock_stashes):
    with patch("stashpoint.alias.load_stashes", return_value=mock_stashes):
        runner.invoke(alias_cmd, ["add", "p", "prod"])
    result = runner.invoke(alias_cmd, ["remove", "p"])
    assert result.exit_code == 0
    assert "removed" in result.output
