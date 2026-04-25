"""Trigger system: run stashpoint actions when entering/leaving directories."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

TRIGGER_FILE = ".stashpoint-trigger.json"


class TriggerNotFoundError(Exception):
    pass


def get_trigger_path() -> Path:
    """Return the path to the global trigger registry."""
    base = Path(os.environ.get("STASHPOINT_DIR", Path.home() / ".stashpoint"))
    base.mkdir(parents=True, exist_ok=True)
    return base / "triggers.json"


def load_triggers() -> dict:
    path = get_trigger_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_triggers(triggers: dict) -> None:
    get_trigger_path().write_text(json.dumps(triggers, indent=2))


def register_trigger(directory: str, stash_name: str, event: str = "enter") -> None:
    """Register a stash to load when entering or leaving a directory.

    Args:
        directory: Absolute path of the directory to watch.
        stash_name: Name of the stash to activate.
        event: 'enter' or 'leave'.
    """
    if event not in ("enter", "leave"):
        raise ValueError(f"event must be 'enter' or 'leave', got {event!r}")
    directory = str(Path(directory).resolve())
    triggers = load_triggers()
    triggers.setdefault(directory, {})[event] = stash_name
    save_triggers(triggers)


def unregister_trigger(directory: str, event: Optional[str] = None) -> None:
    """Remove a trigger for a directory. If event is None, remove all events."""
    directory = str(Path(directory).resolve())
    triggers = load_triggers()
    if directory not in triggers:
        raise TriggerNotFoundError(f"No trigger registered for {directory!r}")
    if event is None:
        del triggers[directory]
    else:
        triggers[directory].pop(event, None)
        if not triggers[directory]:
            del triggers[directory]
    save_triggers(triggers)


def get_trigger(directory: str, event: str) -> Optional[str]:
    """Return the stash name for a directory+event pair, or None."""
    directory = str(Path(directory).resolve())
    triggers = load_triggers()
    return triggers.get(directory, {}).get(event)


def list_triggers() -> list[dict]:
    """Return a flat list of all registered triggers."""
    triggers = load_triggers()
    result = []
    for directory, events in sorted(triggers.items()):
        for event, stash_name in sorted(events.items()):
            result.append({"directory": directory, "event": event, "stash": stash_name})
    return result
