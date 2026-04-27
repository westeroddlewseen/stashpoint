"""Visibility control for stashes (public/private/shared)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

VISIBILITY_LEVELS = ("private", "shared", "public")


class StashNotFoundError(Exception):
    pass


class InvalidVisibilityError(Exception):
    pass


def get_visibility_path() -> Path:
    base = Path.home() / ".stashpoint"
    base.mkdir(parents=True, exist_ok=True)
    return base / "visibility.json"


def load_visibility() -> Dict[str, str]:
    path = get_visibility_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def save_visibility(data: Dict[str, str]) -> None:
    path = get_visibility_path()
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_visibility(stash_name: str, level: str, *, stashes: Optional[Dict] = None) -> str:
    """Set visibility level for a stash. Returns the new level."""
    if level not in VISIBILITY_LEVELS:
        raise InvalidVisibilityError(
            f"Invalid visibility '{level}'. Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    if stashes is not None and stash_name not in stashes:
        raise StashNotFoundError(f"Stash '{stash_name}' not found.")
    data = load_visibility()
    data[stash_name] = level
    save_visibility(data)
    return level


def get_visibility(stash_name: str) -> str:
    """Return the visibility level for a stash (defaults to 'private')."""
    data = load_visibility()
    return data.get(stash_name, "private")


def remove_visibility(stash_name: str) -> bool:
    """Remove explicit visibility setting. Returns True if removed."""
    data = load_visibility()
    if stash_name not in data:
        return False
    del data[stash_name]
    save_visibility(data)
    return True


def list_by_visibility(level: str) -> list:
    """Return all stash names with the given visibility level."""
    if level not in VISIBILITY_LEVELS:
        raise InvalidVisibilityError(
            f"Invalid visibility '{level}'. Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    data = load_visibility()
    return sorted(name for name, lvl in data.items() if lvl == level)
