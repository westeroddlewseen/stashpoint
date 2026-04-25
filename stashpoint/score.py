"""Scoring/ranking module for stashpoint stashes.

Assigns a numeric score to each stash based on usage signals such as
recency of access, number of variables, pin status, and tag count.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from stashpoint.storage import load_stashes
from stashpoint.pin import load_pins
from stashpoint.tag import load_tags
from stashpoint.history import load_history


@dataclass
class StashScore:
    name: str
    score: float
    var_count: int
    event_count: int
    is_pinned: bool
    tag_count: int


# Weights used when computing the composite score
_W_EVENTS = 2.0
_W_VARS = 0.5
_W_PINNED = 5.0
_W_TAGS = 1.0


def score_stash(name: str) -> StashScore:
    """Compute a score for a single stash."""
    stashes = load_stashes()
    if name not in stashes:
        raise KeyError(f"Stash '{name}' not found.")

    variables = stashes[name]
    var_count = len(variables)

    pins = load_pins()
    is_pinned = name in pins

    tags = load_tags()
    tag_count = len(tags.get(name, []))

    history = load_history()
    event_count = sum(1 for e in history if e.get("stash") == name)

    score = (
        _W_EVENTS * event_count
        + _W_VARS * var_count
        + (_W_PINNED if is_pinned else 0.0)
        + _W_TAGS * tag_count
    )

    return StashScore(
        name=name,
        score=round(score, 2),
        var_count=var_count,
        event_count=event_count,
        is_pinned=is_pinned,
        tag_count=tag_count,
    )


def rank_stashes() -> List[StashScore]:
    """Return all stashes ranked from highest to lowest score."""
    stashes = load_stashes()
    scores = [score_stash(name) for name in stashes]
    scores.sort(key=lambda s: s.score, reverse=True)
    return scores
