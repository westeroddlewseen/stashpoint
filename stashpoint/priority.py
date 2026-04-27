"""Priority management for stashes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from stashpoint.storage import load_stashes

MIN_PRIORITY = 1
MAX_PRIORITY = 10
DEFAULT_PRIORITY = 5


class StashNotFoundError(Exception):
    pass


class InvalidPriorityError(Exception):
    pass


def get_priority_path() -> Path:
    from stashpoint.storage import get_stash_path
    return get_stash_path().parent / "priorities.json"


def load_priorities() -> Dict[str, int]:
    path = get_priority_path()
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_priorities(priorities: Dict[str, int]) -> None:
    path = get_priority_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(priorities, f, indent=2)


def set_priority(name: str, level: int, *, check_exists: bool = True) -> int:
    if check_exists:
        stashes = load_stashes()
        if name not in stashes:
            raise StashNotFoundError(f"Stash '{name}' not found.")
    if not (MIN_PRIORITY <= level <= MAX_PRIORITY):
        raise InvalidPriorityError(
            f"Priority must be between {MIN_PRIORITY} and {MAX_PRIORITY}, got {level}."
        )
    priorities = load_priorities()
    priorities[name] = level
    save_priorities(priorities)
    return level


def get_priority(name: str) -> int:
    priorities = load_priorities()
    return priorities.get(name, DEFAULT_PRIORITY)


def remove_priority(name: str) -> bool:
    priorities = load_priorities()
    if name not in priorities:
        return False
    del priorities[name]
    save_priorities(priorities)
    return True


def rank_by_priority(names: List[str]) -> List[str]:
    """Return stash names sorted by priority descending (highest first)."""
    priorities = load_priorities()
    return sorted(names, key=lambda n: priorities.get(n, DEFAULT_PRIORITY), reverse=True)
