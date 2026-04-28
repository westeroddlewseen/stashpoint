"""Cooldown enforcement for stash operations.

Prevents a stash from being overwritten more frequently than a configured
minimum interval (in seconds).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_stashes


class StashNotFoundError(Exception):
    pass


class CooldownActiveError(Exception):
    """Raised when a stash is still within its cooldown period."""

    def __init__(self, name: str, remaining: float) -> None:
        self.name = name
        self.remaining = remaining
        super().__init__(
            f"Stash '{name}' is on cooldown for {remaining:.1f} more second(s)."
        )


def get_cooldown_path() -> Path:
    return get_stash_path().parent / "cooldowns.json"


def load_cooldowns() -> dict:
    path = get_cooldown_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def save_cooldowns(data: dict) -> None:
    path = get_cooldown_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_cooldown(name: str, seconds: int, *, check_exists: bool = True) -> None:
    """Register a cooldown interval (in seconds) for *name*."""
    if check_exists:
        stashes = load_stashes()
        if name not in stashes:
            raise StashNotFoundError(f"Stash '{name}' does not exist.")
    if seconds <= 0:
        raise ValueError("Cooldown must be a positive integer.")
    data = load_cooldowns()
    data[name] = {"interval": seconds, "last_write": None}
    save_cooldowns(data)


def clear_cooldown(name: str) -> bool:
    """Remove cooldown for *name*. Returns True if an entry existed."""
    data = load_cooldowns()
    if name not in data:
        return False
    del data[name]
    save_cooldowns(data)
    return True


def record_write(name: str) -> None:
    """Record that *name* was just written. Call after a successful save."""
    data = load_cooldowns()
    if name in data:
        data[name]["last_write"] = time.time()
        save_cooldowns(data)


def check_cooldown(name: str) -> Optional[float]:
    """Return remaining cooldown seconds, or None if no cooldown is active."""
    data = load_cooldowns()
    entry = data.get(name)
    if entry is None:
        return None
    last = entry.get("last_write")
    if last is None:
        return None
    elapsed = time.time() - last
    remaining = entry["interval"] - elapsed
    return remaining if remaining > 0 else None


def enforce_cooldown(name: str) -> None:
    """Raise CooldownActiveError if the stash is within its cooldown period."""
    remaining = check_cooldown(name)
    if remaining is not None:
        raise CooldownActiveError(name, remaining)
