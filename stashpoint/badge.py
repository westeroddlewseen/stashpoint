"""Badge system: assign visual badges to stashes based on criteria."""

from dataclasses import dataclass, field
from typing import Optional
from stashpoint.storage import load_stashes
from stashpoint.history import load_history
from stashpoint.favorite import load_favorites
from stashpoint.rating import load_ratings


class StashNotFoundError(Exception):
    pass


BADGE_DEFINITIONS = {
    "starred":    "⭐  Starred — stash is marked as a favorite",
    "veteran":    "🏅  Veteran — stash has 10 or more history events",
    "rich":       "💎  Rich — stash has 20 or more variables",
    "top-rated":  "🥇  Top-Rated — stash has a rating of 5",
    "minimalist": "🌿  Minimalist — stash has 3 or fewer variables",
    "active":     "🔥  Active — stash has 5 or more history events in the last 7 days",
}


@dataclass
class BadgeResult:
    stash_name: str
    badges: list = field(default_factory=list)


def _event_count(history: list, stash_name: str) -> int:
    return sum(1 for e in history if e.get("stash") == stash_name)


def _recent_event_count(history: list, stash_name: str, days: int = 7) -> int:
    import time
    cutoff = time.time() - days * 86400
    return sum(
        1 for e in history
        if e.get("stash") == stash_name and e.get("timestamp", 0) >= cutoff
    )


def compute_badges(stash_name: str) -> BadgeResult:
    """Compute all earned badges for a given stash."""
    stashes = load_stashes()
    if stash_name not in stashes:
        raise StashNotFoundError(f"Stash '{stash_name}' not found.")

    variables = stashes[stash_name]
    history = load_history()
    favorites = load_favorites()
    ratings = load_ratings()

    badges = []

    if stash_name in favorites:
        badges.append("starred")

    if _event_count(history, stash_name) >= 10:
        badges.append("veteran")

    if len(variables) >= 20:
        badges.append("rich")
    elif len(variables) <= 3:
        badges.append("minimalist")

    if ratings.get(stash_name) == 5:
        badges.append("top-rated")

    if _recent_event_count(history, stash_name) >= 5:
        badges.append("active")

    return BadgeResult(stash_name=stash_name, badges=badges)


def format_badges(result: BadgeResult) -> str:
    """Return a human-readable badge report."""
    if not result.badges:
        return f"No badges earned for '{result.stash_name}'."
    lines = [f"Badges for '{result.stash_name}':"]
    for badge in result.badges:
        lines.append(f"  {BADGE_DEFINITIONS.get(badge, badge)}")
    return "\n".join(lines)
