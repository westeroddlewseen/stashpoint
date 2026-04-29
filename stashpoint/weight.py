"""Assign and retrieve numeric weights for stashes (used for prioritised ordering)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from stashpoint.storage import load_stashes


class StashNotFoundError(Exception):
    pass


class InvalidWeightError(Exception):
    pass


WEIGHT_MIN = 0
WEIGHT_MAX = 1000


def get_weight_path() -> Path:
    from stashpoint.storage import get_stash_path
    return get_stash_path().parent / "weights.json"


def load_weights() -> Dict[str, int]:
    path = get_weight_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def save_weights(weights: Dict[str, int]) -> None:
    path = get_weight_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(weights, fh, indent=2)


def set_weight(name: str, value: int, *, check_exists: bool = True) -> int:
    """Set the weight for *name* and return the stored value."""
    if check_exists:
        stashes = load_stashes()
        if name not in stashes:
            raise StashNotFoundError(f"Stash '{name}' not found.")
    if not isinstance(value, int) or isinstance(value, bool):
        raise InvalidWeightError(f"Weight must be an integer, got {type(value).__name__}.")
    if not (WEIGHT_MIN <= value <= WEIGHT_MAX):
        raise InvalidWeightError(
            f"Weight must be between {WEIGHT_MIN} and {WEIGHT_MAX}, got {value}."
        )
    weights = load_weights()
    weights[name] = value
    save_weights(weights)
    return value


def get_weight(name: str, default: int = 500) -> int:
    """Return the weight for *name*, or *default* if not set."""
    return load_weights().get(name, default)


def remove_weight(name: str) -> bool:
    """Remove the weight entry for *name*. Returns True if it existed."""
    weights = load_weights()
    if name in weights:
        del weights[name]
        save_weights(weights)
        return True
    return False


def ranked_stashes(default: int = 500) -> List[Tuple[str, int]]:
    """Return all known stashes sorted descending by weight."""
    stashes = load_stashes()
    weights = load_weights()
    ranked = [(n, weights.get(n, default)) for n in stashes]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked
