"""Rating system for stashes — allows users to assign a 1-5 star rating to any stash."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_stashes


class StashNotFoundError(Exception):
    pass


class InvalidRatingError(Exception):
    pass


MIN_RATING = 1
MAX_RATING = 5


def get_rating_path() -> Path:
    return get_stash_path().parent / "ratings.json"


def load_ratings() -> dict[str, int]:
    path = get_rating_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def save_ratings(ratings: dict[str, int]) -> None:
    path = get_rating_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(ratings, f, indent=2)


def rate_stash(name: str, rating: int, *, check_exists: bool = True) -> int:
    """Assign a rating (1-5) to a stash. Returns the stored rating."""
    if check_exists:
        stashes = load_stashes()
        if name not in stashes:
            raise StashNotFoundError(f"Stash '{name}' not found.")
    if not isinstance(rating, int) or not (MIN_RATING <= rating <= MAX_RATING):
        raise InvalidRatingError(
            f"Rating must be an integer between {MIN_RATING} and {MAX_RATING}, got {rating!r}."
        )
    ratings = load_ratings()
    ratings[name] = rating
    save_ratings(ratings)
    return rating


def get_rating(name: str) -> Optional[int]:
    """Return the rating for a stash, or None if unrated."""
    return load_ratings().get(name)


def remove_rating(name: str) -> bool:
    """Remove the rating for a stash. Returns True if a rating existed."""
    ratings = load_ratings()
    if name in ratings:
        del ratings[name]
        save_ratings(ratings)
        return True
    return False


def get_top_rated(limit: int = 10) -> list[tuple[str, int]]:
    """Return stashes sorted by rating descending, up to *limit* entries."""
    ratings = load_ratings()
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    return sorted_ratings[:limit]
