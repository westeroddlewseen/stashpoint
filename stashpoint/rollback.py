"""Rollback a stash to a previous state using history events."""

from stashpoint.storage import load_stash, save_stash, load_stashes
from stashpoint.history import load_history


class StashNotFoundError(Exception):
    pass


class RollbackPointNotFoundError(Exception):
    pass


def list_rollback_points(stash_name: str) -> list[dict]:
    """Return history events for a stash that can be rolled back to."""
    history = load_history()
    events = [
        e for e in history
        if e.get("stash") == stash_name and e.get("action") == "save"
    ]
    return list(reversed(events))


def rollback_stash(stash_name: str, index: int, overwrite: bool = False) -> dict:
    """Restore a stash to the variables captured at a prior save event.

    Args:
        stash_name: Name of the stash to roll back.
        index: Zero-based index into the rollback point list (0 = most recent).
        overwrite: If False, raises if the stash currently exists.

    Returns:
        The restored variables dict.
    """
    stashes = load_stashes()
    if stash_name not in stashes and not overwrite:
        raise StashNotFoundError(f"Stash '{stash_name}' not found.")

    points = list_rollback_points(stash_name)
    if not points:
        raise RollbackPointNotFoundError(
            f"No rollback points found for stash '{stash_name}'."
        )
    if index >= len(points):
        raise RollbackPointNotFoundError(
            f"Rollback index {index} out of range (0–{len(points) - 1})."
        )

    point = points[index]
    snapshot = point.get("snapshot")
    if snapshot is None:
        raise RollbackPointNotFoundError(
            f"Rollback point {index} has no snapshot data."
        )

    save_stash(stash_name, snapshot)
    return snapshot


def get_rollback_summary(stash_name: str) -> str:
    """Return a human-readable summary of available rollback points."""
    points = list_rollback_points(stash_name)
    if not points:
        return f"No rollback points available for '{stash_name}'."
    lines = [f"Rollback points for '{stash_name}':"]
    for i, p in enumerate(points):
        ts = p.get("timestamp", "unknown")
        count = len(p.get("snapshot", {}))
        lines.append(f"  [{i}] {ts} — {count} variable(s)")
    return "\n".join(lines)
