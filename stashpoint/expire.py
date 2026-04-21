"""Expiry support for stashes — set a TTL and check/purge expired stashes."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_stashes, save_stashes


class StashNotFoundError(Exception):
    pass


def get_expiry_path() -> Path:
    base = get_stash_path().parent
    return base / "expiry.json"


def load_expiry() -> dict[str, float]:
    path = get_expiry_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def save_expiry(data: dict[str, float]) -> None:
    path = get_expiry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_expiry(stash_name: str, ttl_seconds: float) -> float:
    """Set a TTL (seconds from now) on a stash. Returns the expiry timestamp."""
    stashes = load_stashes()
    if stash_name not in stashes:
        raise StashNotFoundError(f"Stash '{stash_name}' not found.")
    expires_at = time.time() + ttl_seconds
    expiry = load_expiry()
    expiry[stash_name] = expires_at
    save_expiry(expiry)
    return expires_at


def clear_expiry(stash_name: str) -> bool:
    """Remove expiry for a stash. Returns True if an entry was removed."""
    expiry = load_expiry()
    if stash_name in expiry:
        del expiry[stash_name]
        save_expiry(expiry)
        return True
    return False


def get_expiry(stash_name: str) -> Optional[float]:
    """Return the expiry timestamp for a stash, or None if not set."""
    return load_expiry().get(stash_name)


def is_expired(stash_name: str) -> bool:
    """Return True if the stash has an expiry that has passed."""
    ts = get_expiry(stash_name)
    if ts is None:
        return False
    return time.time() >= ts


def purge_expired() -> list[str]:
    """Delete all expired stashes. Returns list of purged stash names."""
    expiry = load_expiry()
    stashes = load_stashes()
    now = time.time()
    purged = []
    for name, ts in list(expiry.items()):
        if now >= ts:
            stashes.pop(name, None)
            del expiry[name]
            purged.append(name)
    if purged:
        save_stashes(stashes)
        save_expiry(expiry)
    return purged
