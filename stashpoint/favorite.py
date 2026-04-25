"""Manage favorite (starred) stashes."""

import json
from pathlib import Path
from typing import List

FAVORITES_FILENAME = "favorites.json"


class StashNotFoundError(Exception):
    pass


class AlreadyFavoritedError(Exception):
    pass


def get_favorite_path() -> Path:
    base = Path.home() / ".stashpoint"
    base.mkdir(parents=True, exist_ok=True)
    return base / FAVORITES_FILENAME


def load_favorites() -> List[str]:
    path = get_favorite_path()
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def save_favorites(favorites: List[str]) -> None:
    path = get_favorite_path()
    with open(path, "w") as f:
        json.dump(sorted(set(favorites)), f, indent=2)


def add_favorite(name: str, stashes: dict, overwrite: bool = False) -> None:
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' does not exist.")
    favorites = load_favorites()
    if name in favorites and not overwrite:
        raise AlreadyFavoritedError(f"Stash '{name}' is already a favorite.")
    if name not in favorites:
        favorites.append(name)
    save_favorites(favorites)


def remove_favorite(name: str) -> bool:
    favorites = load_favorites()
    if name not in favorites:
        return False
    favorites.remove(name)
    save_favorites(favorites)
    return True


def list_favorites() -> List[str]:
    return load_favorites()


def is_favorite(name: str) -> bool:
    return name in load_favorites()
