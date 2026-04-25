"""Label support for stashes — attach short human-readable display labels."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from stashpoint.storage import load_stashes


class StashNotFoundError(Exception):
    pass


class LabelNotFoundError(Exception):
    pass


def get_label_path() -> Path:
    from stashpoint.storage import get_stash_path
    return get_stash_path().parent / "labels.json"


def load_labels() -> Dict[str, str]:
    path = get_label_path()
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def save_labels(labels: Dict[str, str]) -> None:
    path = get_label_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(labels, fh, indent=2)


def set_label(stash_name: str, label: str, *, check_exists: bool = True) -> None:
    if check_exists:
        stashes = load_stashes()
        if stash_name not in stashes:
            raise StashNotFoundError(f"Stash '{stash_name}' not found.")
    labels = load_labels()
    labels[stash_name] = label
    save_labels(labels)


def get_label(stash_name: str) -> Optional[str]:
    labels = load_labels()
    return labels.get(stash_name)


def remove_label(stash_name: str) -> None:
    labels = load_labels()
    if stash_name not in labels:
        raise LabelNotFoundError(f"No label set for stash '{stash_name}'.")
    del labels[stash_name]
    save_labels(labels)


def list_labels() -> Dict[str, str]:
    return load_labels()
