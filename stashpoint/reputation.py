"""Reputation scoring for stashes based on usage signals."""

from dataclasses import dataclass, field
from typing import List

from stashpoint.storage import load_stashes
from stashpoint.history import load_history
from stashpoint.favorite import load_favorites
from stashpoint.rating import load_ratings
from stashpoint.tag import load_tags


class StashNotFoundError(Exception):
    pass


@dataclass
class ReputationResult:
    name: str
    score: float
    grade: str
    signals: List[str] = field(default_factory=list)


def _grade(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"


def compute_reputation(
    name: str,
    _load_stashes=load_stashes,
    _load_history=load_history,
    _load_favorites=load_favorites,
    _load_ratings=load_ratings,
    _load_tags=load_tags,
) -> ReputationResult:
    """Compute a reputation score for a stash from multiple signals."""
    stashes = _load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    score = 0.0
    signals: List[str] = []

    # Signal: variable count (up to 20 pts)
    var_count = len(stashes[name])
    var_pts = min(var_count * 4, 20)
    if var_pts > 0:
        score += var_pts
        signals.append(f"+{var_pts} pts: {var_count} variable(s) defined")

    # Signal: usage history (up to 30 pts)
    history = _load_history()
    events = [e for e in history if e.get("stash") == name]
    history_pts = min(len(events) * 3, 30)
    if history_pts > 0:
        score += history_pts
        signals.append(f"+{history_pts} pts: {len(events)} history event(s)")

    # Signal: favorited (15 pts)
    favorites = _load_favorites()
    if name in favorites:
        score += 15
        signals.append("+15 pts: marked as favorite")

    # Signal: user rating (up to 25 pts)
    ratings = _load_ratings()
    if name in ratings:
        rating = ratings[name]
        rating_pts = round((rating / 5.0) * 25)
        score += rating_pts
        signals.append(f"+{rating_pts} pts: user rating {rating}/5")

    # Signal: has tags (10 pts)
    tags = _load_tags()
    if tags.get(name):
        score += 10
        signals.append(f"+10 pts: {len(tags[name])} tag(s) applied")

    score = min(score, 100.0)
    return ReputationResult(name=name, score=score, grade=_grade(score), signals=signals)
