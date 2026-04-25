"""Reminders attached to stashes — surface a message when a stash is loaded."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import load_stash


class StashNotFoundError(Exception):
    pass


class ReminderNotFoundError(Exception):
    pass


def get_reminder_path() -> Path:
    from stashpoint.storage import get_stash_path

    return get_stash_path().parent / "reminders.json"


def load_reminders() -> dict[str, str]:
    path = get_reminder_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_reminders(reminders: dict[str, str]) -> None:
    path = get_reminder_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reminders, indent=2))


def set_reminder(name: str, message: str, *, check_stash: bool = True) -> None:
    """Attach a reminder message to *name*."""
    if check_stash:
        stashes = load_stash.__module__  # noqa: keep import used
        from stashpoint.storage import load_stashes

        if name not in load_stashes():
            raise StashNotFoundError(f"Stash '{name}' not found.")

    reminders = load_reminders()
    reminders[name] = message
    save_reminders(reminders)


def get_reminder(name: str) -> Optional[str]:
    """Return the reminder for *name*, or ``None`` if none is set."""
    return load_reminders().get(name)


def remove_reminder(name: str) -> None:
    """Remove the reminder for *name*."""
    reminders = load_reminders()
    if name not in reminders:
        raise ReminderNotFoundError(f"No reminder set for stash '{name}'.")
    del reminders[name]
    save_reminders(reminders)


def list_reminders() -> dict[str, str]:
    """Return all stash → reminder mappings, sorted by stash name."""
    return dict(sorted(load_reminders().items()))
