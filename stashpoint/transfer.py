"""Transfer stashes between different stash directories (e.g. projects)."""

import os
import shutil
from pathlib import Path

from stashpoint.storage import load_stash, save_stash, load_stashes


class StashNotFoundError(Exception):
    pass


class StashAlreadyExistsError(Exception):
    pass


class InvalidDirectoryError(Exception):
    pass


def transfer_stash(
    name: str,
    source_dir: str,
    dest_dir: str,
    overwrite: bool = False,
    move: bool = False,
) -> dict:
    """Copy (or move) a stash from source_dir to dest_dir.

    Returns a summary dict with keys: name, source, destination, moved.
    """
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)

    if not source_path.is_dir():
        raise InvalidDirectoryError(f"Source directory not found: {source_dir}")
    if not dest_path.is_dir():
        dest_path.mkdir(parents=True, exist_ok=True)

    # Load stash from source
    source_stashes_file = source_path / "stashes.json"
    if not source_stashes_file.exists():
        raise StashNotFoundError(f"Stash '{name}' not found in {source_dir}")

    import json
    with open(source_stashes_file) as f:
        source_stashes = json.load(f)

    if name not in source_stashes:
        raise StashNotFoundError(f"Stash '{name}' not found in {source_dir}")

    variables = source_stashes[name]

    # Check destination
    dest_stashes_file = dest_path / "stashes.json"
    if dest_stashes_file.exists():
        with open(dest_stashes_file) as f:
            dest_stashes = json.load(f)
    else:
        dest_stashes = {}

    if name in dest_stashes and not overwrite:
        raise StashAlreadyExistsError(
            f"Stash '{name}' already exists in {dest_dir}. Use overwrite=True to replace."
        )

    dest_stashes[name] = variables
    with open(dest_stashes_file, "w") as f:
        json.dump(dest_stashes, f, indent=2)

    if move:
        del source_stashes[name]
        with open(source_stashes_file, "w") as f:
            json.dump(source_stashes, f, indent=2)

    return {
        "name": name,
        "source": str(source_path.resolve()),
        "destination": str(dest_path.resolve()),
        "moved": move,
    }


def list_transfer_targets(dest_dir: str) -> list:
    """Return stash names available in a given directory."""
    stashes_file = Path(dest_dir) / "stashes.json"
    if not stashes_file.exists():
        return []
    import json
    with open(stashes_file) as f:
        data = json.load(f)
    return sorted(data.keys())
