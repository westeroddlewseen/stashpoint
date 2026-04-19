"""Handles persistent storage of named environment variable stashes."""

import json
import os
from pathlib import Path

DEFAULT_STASH_DIR = Path.home() / ".stashpoint"
STASH_FILE = "stashes.json"


def get_stash_path() -> Path:
    """Return the path to the stash file, respecting STASHPOINT_DIR env override."""
    stash_dir = Path(os.environ.get("STASHPOINT_DIR", DEFAULT_STASH_DIR))
    stash_dir.mkdir(parents=True, exist_ok=True)
    return stash_dir / STASH_FILE


def load_stashes() -> dict:
    """Load all stashes from disk. Returns empty dict if file doesn't exist."""
    path = get_stash_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_stashes(stashes: dict) -> None:
    """Persist all stashes to disk."""
    path = get_stash_path()
    with open(path, "w") as f:
        json.dump(stashes, f, indent=2)


def save_stash(name: str, variables: dict) -> None:
    """Save a named stash of environment variables."""
    stashes = load_stashes()
    stashes[name] = variables
    save_stashes(stashes)


def load_stash(name: str) -> dict:
    """Load a named stash. Raises KeyError if not found."""
    stashes = load_stashes()
    if name not in stashes:
        raise KeyError(f"No stash found with name '{name}'")
    return stashes[name]


def delete_stash(name: str) -> None:
    """Delete a named stash. Raises KeyError if not found."""
    stashes = load_stashes()
    if name not in stashes:
        raise KeyError(f"No stash found with name '{name}'")
    del stashes[name]
    save_stashes(stashes)


def list_stashes() -> list:
    """Return a sorted list of all stash names."""
    return sorted(load_stashes().keys())
