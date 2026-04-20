"""Pin management for stashpoint — mark stashes as pinned to prevent accidental deletion."""

import json
from pathlib import Path
from typing import List

STASH_DIR = Path.home() / ".stashpoint"


def get_pin_path() -> Path:
    return STASH_DIR / "pins.json"


def load_pins() -> List[str]:
    path = get_pin_path()
    if not path.exists():
        return []
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("pinned", [])


def save_pins(pinned: List[str]) -> None:
    path = get_pin_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump({"pinned": pinned}, f, indent=2)


def pin_stash(name: str) -> None:
    """Mark a stash as pinned. Idempotent."""
    pinned = load_pins()
    if name not in pinned:
        pinned.append(name)
        save_pins(pinned)


def unpin_stash(name: str) -> None:
    """Remove pin from a stash. Idempotent."""
    pinned = load_pins()
    if name in pinned:
        pinned.remove(name)
        save_pins(pinned)


def is_pinned(name: str) -> bool:
    """Return True if the stash is pinned."""
    return name in load_pins()


def list_pinned() -> List[str]:
    """Return sorted list of pinned stash names."""
    return sorted(load_pins())
