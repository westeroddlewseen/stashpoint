"""CLI tests for the 'note' command group."""

import pytest
from click.testing import CliRunner

from stashpoint.cli_note import note_cmd
from stashpoint.note import NoteNotFoundError, StashNotFoundError


@pytest.fixture()
def runner():
    return CliRunner()


def test_set_note_success(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_note.set_note", lambda n, t: None)
    result = runner.invoke(note_cmd, ["set", "dev", "hello world"])
    assert result.exit_code == 0
    assert "Note set for 'dev'" in result.output


def test_set_note_stash_not_found(runner, monkeypatch):
    def _raise(name, text):
        raise StashNotFoundError(name)

    monkeypatch.setattr("stashpoint.cli_note.set_note", _raise)
    result = runner.invoke(note_cmd, ["set", "missing", "text"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_get_note_success(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_note.get_note", lambda n: "my note")
    result = runner.invoke(note_cmd, ["get", "dev"])
    assert result.exit_code == 0
    assert "my note" in result.output


def test_get_note_not_found(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_note.get_note", lambda n: None)
    result = runner.invoke(note_cmd, ["get", "dev"])
    assert result.exit_code != 0
    assert "No note found" in result.output


def test_remove_note_success(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_note.remove_note", lambda n: None)
    result = runner.invoke(note_cmd, ["remove", "dev"])
    assert result.exit_code == 0
    assert "Note removed for 'dev'" in result.output


def test_remove_note_not_found(runner, monkeypatch):
    def _raise(name):
        raise NoteNotFoundError(name)

    monkeypatch.setattr("stashpoint.cli_note.remove_note", _raise)
    result = runner.invoke(note_cmd, ["remove", "dev"])
    assert result.exit_code != 0
    assert "No note found" in result.output


def test_list_notes_empty(runner, monkeypatch):
    monkeypatch.setattr("stashpoint.cli_note.list_notes", lambda: {})
    result = runner.invoke(note_cmd, ["list"])
    assert result.exit_code == 0
    assert "No notes found" in result.output


def test_list_notes_shows_entries(runner, monkeypatch):
    monkeypatch.setattr(
        "stashpoint.cli_note.list_notes",
        lambda: {"dev": "local env", "prod": "live env"},
    )
    result = runner.invoke(note_cmd, ["list"])
    assert result.exit_code == 0
    assert "dev: local env" in result.output
    assert "prod: live env" in result.output
