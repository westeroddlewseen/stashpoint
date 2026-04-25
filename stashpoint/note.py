"""Attach and retrieve free-form notes on stashes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import load_stashes


class StashNotFoundError(Exception):
    """Raised when the target stash does not exist."""


class NoteNotFoundError(Exception):
    """Raised when no note exists for the given stash."""


def get_note_path() -> Path:
    from stashpoint.storage import get_stash_path

    return get_stash_path().parent / "notes.json"


def load_notes() -> dict[str, str]:
    path = get_note_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_notes(notes: dict[str, str]) -> None:
    path = get_note_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notes, indent=2))


def set_note(stash_name: str, text: str, *, check_exists: bool = True) -> None:
    """Attach *text* as a note on *stash_name*."""
    if check_exists:
        stashes = load_stashes()
        if stash_name not in stashes:
            raise StashNotFoundError(stash_name)
    notes = load_notes()
    notes[stash_name] = text
    save_notes(notes)


def get_note(stash_name: str) -> Optional[str]:
    """Return the note for *stash_name*, or ``None`` if none exists."""
    return load_notes().get(stash_name)


def remove_note(stash_name: str) -> None:
    """Remove the note for *stash_name*.

    Raises :exc:`NoteNotFoundError` if no note is attached.
    """
    notes = load_notes()
    if stash_name not in notes:
        raise NoteNotFoundError(stash_name)
    del notes[stash_name]
    save_notes(notes)


def list_notes() -> dict[str, str]:
    """Return all stash-name → note mappings."""
    return dict(load_notes())
