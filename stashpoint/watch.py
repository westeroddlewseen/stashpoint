"""Watch a stash for changes and trigger actions."""

import time
import hashlib
import json
from typing import Callable, Optional

from stashpoint.storage import load_stash


class StashNotFoundError(Exception):
    pass


def _stash_fingerprint(variables: dict) -> str:
    """Return a stable hash of a stash's contents."""
    serialized = json.dumps(variables, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()


def poll_stash(
    name: str,
    interval: float = 2.0,
    max_polls: Optional[int] = None,
    on_change: Optional[Callable[[str, dict, dict], None]] = None,
) -> None:
    """Poll a stash for changes at a given interval.

    Args:
        name: The stash name to watch.
        interval: Seconds between polls.
        max_polls: Stop after this many polls (None = run forever).
        on_change: Callback invoked with (name, old_vars, new_vars) on change.
    """
    current = load_stash(name)
    if current is None:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    last_fingerprint = _stash_fingerprint(current)
    last_vars = dict(current)
    polls = 0

    while max_polls is None or polls < max_polls:
        time.sleep(interval)
        polls += 1

        fresh = load_stash(name)
        if fresh is None:
            raise StashNotFoundError(f"Stash '{name}' was deleted during watch.")

        new_fingerprint = _stash_fingerprint(fresh)
        if new_fingerprint != last_fingerprint:
            if on_change:
                on_change(name, last_vars, dict(fresh))
            last_vars = dict(fresh)
            last_fingerprint = new_fingerprint


def get_changes(old: dict, new: dict) -> dict:
    """Return a summary of changes between two variable dicts."""
    added = {k: v for k, v in new.items() if k not in old}
    removed = {k: old[k] for k in old if k not in new}
    changed = {k: (old[k], new[k]) for k in old if k in new and old[k] != new[k]}
    return {"added": added, "removed": removed, "changed": changed}
