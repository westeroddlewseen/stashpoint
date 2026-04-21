"""Annotate stashes with human-readable notes/descriptions."""

import json
from pathlib import Path
from stashpoint.storage import get_stash_path


class StashNotFoundError(Exception):
    pass


def get_annotation_path() -> Path:
    base = get_stash_path().parent
    return base / "annotations.json"


def load_annotations() -> dict:
    path = get_annotation_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_annotations(annotations: dict) -> None:
    path = get_annotation_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(annotations, f, indent=2)


def set_annotation(stash_name: str, note: str, stashes: dict = None) -> None:
    """Set or update the annotation for a stash."""
    if stashes is not None and stash_name not in stashes:
        raise StashNotFoundError(f"Stash '{stash_name}' not found.")
    annotations = load_annotations()
    annotations[stash_name] = note
    save_annotations(annotations)


def get_annotation(stash_name: str) -> str | None:
    """Return the annotation for a stash, or None if not set."""
    annotations = load_annotations()
    return annotations.get(stash_name)


def remove_annotation(stash_name: str) -> bool:
    """Remove annotation for a stash. Returns True if it existed."""
    annotations = load_annotations()
    if stash_name in annotations:
        del annotations[stash_name]
        save_annotations(annotations)
        return True
    return False


def list_annotations() -> dict:
    """Return all annotations as a dict of {stash_name: note}."""
    return load_annotations()
