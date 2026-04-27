"""Retention policy management for stashes."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from stashpoint.storage import load_stashes


class StashNotFoundError(Exception):
    pass


class InvalidRetentionError(Exception):
    pass


MAX_RETENTION_DAYS = 3650  # 10 years


def get_retention_path() -> Path:
    base = Path.home() / ".stashpoint"
    base.mkdir(exist_ok=True)
    return base / "retention.json"


def load_retention() -> Dict[str, int]:
    path = get_retention_path()
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_retention(data: Dict[str, int]) -> None:
    with open(get_retention_path(), "w") as f:
        json.dump(data, f, indent=2)


def set_retention(name: str, days: int, *, check_exists: bool = True) -> int:
    """Set a retention policy (in days) for a stash. Returns expiry timestamp."""
    if check_exists:
        stashes = load_stashes()
        if name not in stashes:
            raise StashNotFoundError(f"Stash '{name}' not found.")
    if not isinstance(days, int) or days < 1:
        raise InvalidRetentionError("Retention days must be a positive integer.")
    if days > MAX_RETENTION_DAYS:
        raise InvalidRetentionError(f"Retention days cannot exceed {MAX_RETENTION_DAYS}.")
    expiry = int(time.time()) + days * 86400
    data = load_retention()
    data[name] = expiry
    save_retention(data)
    return expiry


def clear_retention(name: str) -> bool:
    """Remove retention policy for a stash. Returns True if removed, False if not set."""
    data = load_retention()
    if name not in data:
        return False
    del data[name]
    save_retention(data)
    return True


def get_retention(name: str) -> Optional[int]:
    """Return the expiry timestamp for a stash, or None if not set."""
    return load_retention().get(name)


def list_expired(stash_names: Optional[List[str]] = None) -> List[str]:
    """Return names of stashes whose retention has expired."""
    now = int(time.time())
    data = load_retention()
    names = stash_names if stash_names is not None else list(data.keys())
    return [n for n in names if n in data and data[n] <= now]
