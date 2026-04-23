"""Group management for stashpoint — organize stashes into named groups."""

import json
from pathlib import Path
from typing import Dict, List

STASH_DIR = Path.home() / ".stashpoint"
GROUP_FILE = "groups.json"


class GroupNotFoundError(Exception):
    pass


class GroupAlreadyExistsError(Exception):
    pass


def get_group_path() -> Path:
    return STASH_DIR / GROUP_FILE


def load_groups() -> Dict[str, List[str]]:
    path = get_group_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_groups(groups: Dict[str, List[str]]) -> None:
    path = get_group_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(groups, f, indent=2)


def create_group(name: str, overwrite: bool = False) -> None:
    groups = load_groups()
    if name in groups and not overwrite:
        raise GroupAlreadyExistsError(f"Group '{name}' already exists.")
    groups[name] = []
    save_groups(groups)


def delete_group(name: str) -> None:
    groups = load_groups()
    if name not in groups:
        raise GroupNotFoundError(f"Group '{name}' not found.")
    del groups[name]
    save_groups(groups)


def add_stash_to_group(group: str, stash: str) -> None:
    groups = load_groups()
    if group not in groups:
        raise GroupNotFoundError(f"Group '{group}' not found.")
    if stash not in groups[group]:
        groups[group].append(stash)
        save_groups(groups)


def remove_stash_from_group(group: str, stash: str) -> None:
    groups = load_groups()
    if group not in groups:
        raise GroupNotFoundError(f"Group '{group}' not found.")
    if stash in groups[group]:
        groups[group].remove(stash)
        save_groups(groups)


def get_group_members(group: str) -> List[str]:
    groups = load_groups()
    if group not in groups:
        raise GroupNotFoundError(f"Group '{group}' not found.")
    return list(groups[group])


def list_groups() -> List[str]:
    return sorted(load_groups().keys())
