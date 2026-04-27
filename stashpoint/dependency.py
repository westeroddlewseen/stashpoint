"""Stash dependency tracking — record that one stash depends on another."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class StashNotFoundError(Exception):
    pass


class CircularDependencyError(Exception):
    pass


class DependencyAlreadyExistsError(Exception):
    pass


def get_dependency_path() -> Path:
    from stashpoint.storage import get_stash_path

    return get_stash_path().parent / "dependencies.json"


def load_dependencies() -> Dict[str, List[str]]:
    path = get_dependency_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def save_dependencies(deps: Dict[str, List[str]]) -> None:
    path = get_dependency_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(deps, fh, indent=2)


def add_dependency(stash: str, depends_on: str, *, check_exists=True) -> None:
    """Record that *stash* depends on *depends_on*."""
    from stashpoint.storage import load_stashes

    if check_exists:
        stashes = load_stashes()
        if stash not in stashes:
            raise StashNotFoundError(stash)
        if depends_on not in stashes:
            raise StashNotFoundError(depends_on)

    deps = load_dependencies()
    current = deps.get(stash, [])
    if depends_on in current:
        raise DependencyAlreadyExistsError(depends_on)

    # Cycle detection: would adding this edge create a cycle?
    if _would_create_cycle(deps, stash, depends_on):
        raise CircularDependencyError(
            f"Adding '{depends_on}' as dependency of '{stash}' would create a cycle."
        )

    deps[stash] = current + [depends_on]
    save_dependencies(deps)


def remove_dependency(stash: str, depends_on: str) -> bool:
    """Remove a dependency edge. Returns True if removed, False if not found."""
    deps = load_dependencies()
    current = deps.get(stash, [])
    if depends_on not in current:
        return False
    deps[stash] = [d for d in current if d != depends_on]
    if not deps[stash]:
        del deps[stash]
    save_dependencies(deps)
    return True


def get_dependencies(stash: str) -> List[str]:
    """Return direct dependencies of *stash*."""
    return load_dependencies().get(stash, [])


def get_dependents(stash: str) -> List[str]:
    """Return stashes that directly depend on *stash*."""
    return [s for s, deps in load_dependencies().items() if stash in deps]


def _would_create_cycle(deps: Dict[str, List[str]], stash: str, new_dep: str) -> bool:
    """DFS from new_dep; if we can reach stash, adding the edge creates a cycle."""
    visited: set = set()
    stack = [new_dep]
    while stack:
        node = stack.pop()
        if node == stash:
            return True
        if node in visited:
            continue
        visited.add(node)
        stack.extend(deps.get(node, []))
    return False
