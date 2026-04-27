"""TTL (time-to-live) support for stashes — auto-expire after a duration."""

import time
from stashpoint.storage import load_stashes, get_stash_path
from pathlib import Path
import json

TTL_FILENAME = "ttl.json"


class StashNotFoundError(Exception):
    pass


class InvalidTTLError(Exception):
    pass


def get_ttl_path() -> Path:
    return get_stash_path().parent / TTL_FILENAME


def load_ttl() -> dict:
    path = get_ttl_path()
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_ttl(data: dict) -> None:
    path = get_ttl_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_ttl(name: str, seconds: int) -> float:
    """Set a TTL in seconds for a stash. Returns the expiry timestamp."""
    if seconds <= 0:
        raise InvalidTTLError(f"TTL must be a positive integer, got {seconds}")
    stashes = load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found")
    expires_at = time.time() + seconds
    data = load_ttl()
    data[name] = {"seconds": seconds, "expires_at": expires_at}
    save_ttl(data)
    return expires_at


def get_ttl(name: str) -> dict | None:
    """Return TTL info for a stash, or None if not set."""
    data = load_ttl()
    return data.get(name)


def clear_ttl(name: str) -> bool:
    """Remove TTL for a stash. Returns True if removed, False if not set."""
    data = load_ttl()
    if name not in data:
        return False
    del data[name]
    save_ttl(data)
    return True


def is_expired(name: str) -> bool:
    """Return True if the stash TTL has passed."""
    entry = get_ttl(name)
    if entry is None:
        return False
    return time.time() >= entry["expires_at"]


def list_expired() -> list[str]:
    """Return names of all stashes whose TTL has expired."""
    data = load_ttl()
    now = time.time()
    return [name for name, entry in data.items() if now >= entry["expires_at"]]
