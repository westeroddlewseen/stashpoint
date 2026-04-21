"""Prune stashes based on criteria such as age, tags, or lock status."""

from datetime import datetime, timezone
from typing import Optional

from stashpoint.storage import load_stashes, save_stashes
from stashpoint.lock import is_locked
from stashpoint.history import load_history
from stashpoint.pin import is_pinned


class PruneError(Exception):
    pass


def get_stash_last_used(name: str) -> Optional[datetime]:
    """Return the most recent timestamp for a stash from history, or None."""
    history = load_history()
    events = [e for e in history if e.get("stash") == name]
    if not events:
        return None
    latest = max(events, key=lambda e: e.get("timestamp", ""))
    ts = latest.get("timestamp")
    if ts:
        return datetime.fromisoformat(ts)
    return None


def prune_stashes(
    dry_run: bool = False,
    skip_locked: bool = True,
    skip_pinned: bool = True,
    older_than_days: Optional[int] = None,
    names: Optional[list] = None,
) -> list:
    """
    Remove stashes matching the given criteria.

    Returns a list of stash names that were (or would be) pruned.
    """
    stashes = load_stashes()
    candidates = list(names) if names else list(stashes.keys())
    pruned = []

    now = datetime.now(timezone.utc)

    for name in candidates:
        if name not in stashes:
            continue

        if skip_locked and is_locked(name):
            continue

        if skip_pinned and is_pinned(name):
            continue

        if older_than_days is not None:
            last_used = get_stash_last_used(name)
            if last_used is not None:
                last_used_utc = last_used.replace(tzinfo=timezone.utc) if last_used.tzinfo is None else last_used
                age_days = (now - last_used_utc).days
                if age_days < older_than_days:
                    continue

        pruned.append(name)

    if not dry_run:
        for name in pruned:
            del stashes[name]
        save_stashes(stashes)

    return pruned


def format_prune_summary(pruned: list, dry_run: bool = False) -> str:
    """Format a human-readable summary of pruned stashes."""
    if not pruned:
        return "No stashes matched the prune criteria."
    prefix = "[dry-run] Would remove" if dry_run else "Removed"
    lines = [f"{prefix} {len(pruned)} stash(es):"] + [f"  - {name}" for name in pruned]
    return "\n".join(lines)
