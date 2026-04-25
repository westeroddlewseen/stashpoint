"""Permission (chmod) management for stashes — mark stashes as read-only or read-write."""

import json
from pathlib import Path
from typing import Dict, List

STASH_DIR = Path.home() / ".stashpoint"
CHMOD_FILE = "chmod.json"


class StashNotFoundError(Exception):
    pass


class StashAlreadyReadOnlyError(Exception):
    pass


class StashNotReadOnlyError(Exception):
    pass


def get_chmod_path() -> Path:
    return STASH_DIR / CHMOD_FILE


def load_chmod() -> Dict[str, str]:
    path = get_chmod_path()
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_chmod(data: Dict[str, str]) -> None:
    path = get_chmod_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_readonly(stash_name: str, stashes: Dict) -> None:
    if stash_name not in stashes:
        raise StashNotFoundError(f"Stash '{stash_name}' not found.")
    data = load_chmod()
    if data.get(stash_name) == "readonly":
        raise StashAlreadyReadOnlyError(f"Stash '{stash_name}' is already read-only.")
    data[stash_name] = "readonly"
    save_chmod(data)


def set_readwrite(stash_name: str, stashes: Dict) -> None:
    if stash_name not in stashes:
        raise StashNotFoundError(f"Stash '{stash_name}' not found.")
    data = load_chmod()
    if data.get(stash_name) != "readonly":
        raise StashNotReadOnlyError(f"Stash '{stash_name}' is not read-only.")
    del data[stash_name]
    save_chmod(data)


def is_readonly(stash_name: str) -> bool:
    data = load_chmod()
    return data.get(stash_name) == "readonly"


def list_readonly() -> List[str]:
    data = load_chmod()
    return sorted(name for name, mode in data.items() if mode == "readonly")
