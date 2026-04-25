"""Unit tests for stashpoint.note."""

from unittest.mock import patch

import pytest

from stashpoint.note import (
    NoteNotFoundError,
    StashNotFoundError,
    get_note,
    list_notes,
    remove_note,
    set_note,
)

_STASHES = {"dev": {"FOO": "bar"}, "prod": {"FOO": "baz"}}


@pytest.fixture()
def mock_notes(tmp_path, monkeypatch):
    """Redirect note storage to a temp file and seed with empty notes."""
    note_file = tmp_path / "notes.json"
    monkeypatch.setattr("stashpoint.note.get_note_path", lambda: note_file)
    monkeypatch.setattr("stashpoint.note.load_stashes", lambda: dict(_STASHES))
    return note_file


def test_get_note_missing_returns_none(mock_notes):
    assert get_note("dev") is None


def test_set_and_get_note(mock_notes):
    set_note("dev", "used for local development")
    assert get_note("dev") == "used for local development"


def test_set_note_stash_not_found(mock_notes):
    with pytest.raises(StashNotFoundError):
        set_note("nonexistent", "some note")


def test_set_note_no_stash_check(mock_notes):
    """check_exists=False should bypass the stash lookup."""
    set_note("ghost", "phantom note", check_exists=False)
    assert get_note("ghost") == "phantom note"


def test_set_note_overwrites_existing(mock_notes):
    set_note("dev", "first note")
    set_note("dev", "second note")
    assert get_note("dev") == "second note"


def test_remove_note(mock_notes):
    set_note("dev", "temporary")
    remove_note("dev")
    assert get_note("dev") is None


def test_remove_note_not_found(mock_notes):
    with pytest.raises(NoteNotFoundError):
        remove_note("dev")


def test_list_notes_empty(mock_notes):
    assert list_notes() == {}


def test_list_notes_returns_all(mock_notes):
    set_note("dev", "note a")
    set_note("prod", "note b")
    result = list_notes()
    assert result == {"dev": "note a", "prod": "note b"}


def test_list_notes_is_independent_copy(mock_notes):
    set_note("dev", "original")
    notes = list_notes()
    notes["dev"] = "mutated"
    assert get_note("dev") == "original"
