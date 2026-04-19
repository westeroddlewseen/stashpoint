"""Stash locking — prevent accidental modification of important stashes."""

import json
from pathlib import Path
from stashpoint.storage import get_stash_path


def get_lock_path() -> Path:
    return get_stash_path().parent / "locks.json"


def load_locks() -> list[str]:
    path = get_lock_path()
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def save_locks(locks: list[str]) -> None:
    path = get_lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(locks, f, indent=2)


def lock_stash(name: str) -> None:
    locks = load_locks()
    if name not in locks:
        locks.append(name)
        save_locks(locks)


def unlock_stash(name: str) -> None:
    locks = load_locks()
    if name in locks:
        locks.remove(name)
        save_locks(locks)


def is_locked(name: str) -> bool:
    return name in load_locks()


def assert_not_locked(name: str) -> None:
    if is_locked(name):
        raise PermissionError(f"Stash '{name}' is locked. Unlock it first.")
