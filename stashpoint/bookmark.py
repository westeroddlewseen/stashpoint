"""Bookmark support: mark stashes for quick access."""

import json
from pathlib import Path
from typing import List

from stashpoint.storage import load_stashes


class StashNotFoundError(Exception):
    pass


class AlreadyBookmarkedError(Exception):
    pass


def get_bookmark_path() -> Path:
    from stashpoint.storage import get_stash_path
    return get_stash_path().parent / "bookmarks.json"


def load_bookmarks() -> List[str]:
    path = get_bookmark_path()
    if not path.exists():
        return []
    with path.open() as f:
        return json.load(f)


def save_bookmarks(bookmarks: List[str]) -> None:
    path = get_bookmark_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(bookmarks, f, indent=2)


def add_bookmark(name: str) -> None:
    stashes = load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' does not exist.")
    bookmarks = load_bookmarks()
    if name in bookmarks:
        raise AlreadyBookmarkedError(f"Stash '{name}' is already bookmarked.")
    bookmarks.append(name)
    save_bookmarks(bookmarks)


def remove_bookmark(name: str) -> bool:
    bookmarks = load_bookmarks()
    if name not in bookmarks:
        return False
    bookmarks.remove(name)
    save_bookmarks(bookmarks)
    return True


def is_bookmarked(name: str) -> bool:
    return name in load_bookmarks()


def list_bookmarks() -> List[str]:
    return list(load_bookmarks())
