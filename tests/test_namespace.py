"""Tests for stashpoint.namespace."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from stashpoint.namespace import (
    NamespaceAlreadyExistsError,
    NamespaceNotFoundError,
    add_to_namespace,
    create_namespace,
    delete_namespace,
    get_namespace_stashes,
    list_namespaces,
    remove_from_namespace,
)
from stashpoint.cli_namespace import namespace_cmd


@pytest.fixture
def mock_ns(tmp_path, monkeypatch):
    ns_file = tmp_path / "namespaces.json"
    monkeypatch.setattr("stashpoint.namespace.get_namespace_path", lambda: ns_file)
    monkeypatch.setattr(
        "stashpoint.namespace.get_stash_path",
        lambda: tmp_path / "stashes.json",
    )
    return ns_file


@pytest.fixture
def mock_stashes(monkeypatch):
    stashes = {"alpha": {"FOO": "bar"}, "beta": {"BAZ": "qux"}}
    monkeypatch.setattr("stashpoint.namespace.load_stashes", lambda: stashes)


def test_create_namespace(mock_ns):
    create_namespace("myns")
    data = json.loads(mock_ns.read_text())
    assert "myns" in data
    assert data["myns"] == []


def test_create_namespace_already_exists_raises(mock_ns):
    create_namespace("myns")
    with pytest.raises(NamespaceAlreadyExistsError):
        create_namespace("myns")


def test_create_namespace_overwrite(mock_ns, mock_stashes):
    create_namespace("myns")
    add_to_namespace("myns", "alpha")
    create_namespace("myns", overwrite=True)
    assert get_namespace_stashes("myns") == []


def test_delete_namespace(mock_ns):
    create_namespace("myns")
    delete_namespace("myns")
    assert "myns" not in load_namespaces()


def test_delete_namespace_not_found(mock_ns):
    with pytest.raises(NamespaceNotFoundError):
        delete_namespace("ghost")


def test_add_to_namespace(mock_ns, mock_stashes):
    create_namespace("myns")
    add_to_namespace("myns", "alpha")
    assert "alpha" in get_namespace_stashes("myns")


def test_add_to_namespace_idempotent(mock_ns, mock_stashes):
    create_namespace("myns")
    add_to_namespace("myns", "alpha")
    add_to_namespace("myns", "alpha")
    assert get_namespace_stashes("myns").count("alpha") == 1


def test_add_to_namespace_stash_not_found(mock_ns, mock_stashes):
    create_namespace("myns")
    with pytest.raises(KeyError):
        add_to_namespace("myns", "nonexistent")


def test_remove_from_namespace(mock_ns, mock_stashes):
    create_namespace("myns")
    add_to_namespace("myns", "alpha")
    remove_from_namespace("myns", "alpha")
    assert "alpha" not in get_namespace_stashes("myns")


def test_list_namespaces_sorted(mock_ns):
    create_namespace("zzz")
    create_namespace("aaa")
    assert list_namespaces() == ["aaa", "zzz"]


def test_cli_create_and_list(mock_ns):
    runner = CliRunner()
    result = runner.invoke(namespace_cmd, ["create", "prod"])
    assert result.exit_code == 0
    assert "created" in result.output
    result = runner.invoke(namespace_cmd, ["list"])
    assert "prod" in result.output


def test_cli_show_empty(mock_ns):
    runner = CliRunner()
    runner.invoke(namespace_cmd, ["create", "empty-ns"])
    result = runner.invoke(namespace_cmd, ["show", "empty-ns"])
    assert "empty" in result.output.lower()


def test_cli_show_not_found(mock_ns):
    runner = CliRunner()
    result = runner.invoke(namespace_cmd, ["show", "ghost"])
    assert result.exit_code == 1
