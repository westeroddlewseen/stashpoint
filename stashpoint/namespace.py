"""Namespace support for grouping stashes under a named prefix."""

import json
import os
from pathlib import Path
from typing import Dict, List

from stashpoint.storage import get_stash_path, load_stashes, save_stashes


class NamespaceNotFoundError(Exception):
    pass


class NamespaceAlreadyExistsError(Exception):
    pass


def get_namespace_path() -> Path:
    return get_stash_path().parent / "namespaces.json"


def load_namespaces() -> Dict[str, List[str]]:
    """Return mapping of namespace -> list of stash names."""
    path = get_namespace_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_namespaces(namespaces: Dict[str, List[str]]) -> None:
    path = get_namespace_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(namespaces, f, indent=2)


def create_namespace(name: str, overwrite: bool = False) -> None:
    """Create a new empty namespace."""
    namespaces = load_namespaces()
    if name in namespaces and not overwrite:
        raise NamespaceAlreadyExistsError(f"Namespace '{name}' already exists.")
    namespaces[name] = []
    save_namespaces(namespaces)


def delete_namespace(name: str) -> None:
    """Delete a namespace (does not delete the stashes within it)."""
    namespaces = load_namespaces()
    if name not in namespaces:
        raise NamespaceNotFoundError(f"Namespace '{name}' not found.")
    del namespaces[name]
    save_namespaces(namespaces)


def add_to_namespace(namespace: str, stash_name: str) -> None:
    """Add a stash to a namespace."""
    namespaces = load_namespaces()
    if namespace not in namespaces:
        raise NamespaceNotFoundError(f"Namespace '{namespace}' not found.")
    stashes = load_stashes()
    if stash_name not in stashes:
        raise KeyError(f"Stash '{stash_name}' does not exist.")
    if stash_name not in namespaces[namespace]:
        namespaces[namespace].append(stash_name)
        namespaces[namespace].sort()
    save_namespaces(namespaces)


def remove_from_namespace(namespace: str, stash_name: str) -> None:
    """Remove a stash from a namespace."""
    namespaces = load_namespaces()
    if namespace not in namespaces:
        raise NamespaceNotFoundError(f"Namespace '{namespace}' not found.")
    if stash_name in namespaces[namespace]:
        namespaces[namespace].remove(stash_name)
    save_namespaces(namespaces)


def list_namespaces() -> List[str]:
    """Return sorted list of namespace names."""
    return sorted(load_namespaces().keys())


def get_namespace_stashes(namespace: str) -> List[str]:
    """Return stash names belonging to the given namespace."""
    namespaces = load_namespaces()
    if namespace not in namespaces:
        raise NamespaceNotFoundError(f"Namespace '{namespace}' not found.")
    return list(namespaces[namespace])
