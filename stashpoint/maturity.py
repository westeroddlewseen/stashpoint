"""Compute a maturity score for a stash based on age, usage, and completeness."""

from dataclasses import dataclass
from typing import List

from stashpoint.storage import load_stashes
from stashpoint.history import get_stash_history
from stashpoint.tag import load_tags, get_tags
from stashpoint.annotate import load_annotations, get_annotation


class StashNotFoundError(Exception):
    pass


@dataclass
class MaturityResult:
    name: str
    score: int          # 0–100
    grade: str          # A / B / C / D / F
    var_count: int
    event_count: int
    has_tags: bool
    has_annotation: bool
    reasons: List[str]


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 55:
        return "C"
    if score >= 35:
        return "D"
    return "F"


def compute_maturity(name: str) -> MaturityResult:
    """Return a MaturityResult for *name*, raising StashNotFoundError if absent."""
    stashes = load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    variables = stashes[name]
    var_count = len(variables)
    events = get_stash_history(name)
    event_count = len(events)

    tags = get_tags(name, load_tags())
    has_tags = len(tags) > 0

    annotation = get_annotation(name, "description", load_annotations())
    has_annotation = annotation is not None and annotation.strip() != ""

    score = 0
    reasons: List[str] = []

    # Variables (up to 40 pts)
    if var_count == 0:
        reasons.append("No variables defined.")
    elif var_count >= 5:
        score += 40
    else:
        score += var_count * 8

    # Usage history (up to 30 pts)
    if event_count == 0:
        reasons.append("Never used.")
    elif event_count >= 10:
        score += 30
    else:
        score += event_count * 3

    # Tags (10 pts)
    if has_tags:
        score += 10
    else:
        reasons.append("No tags assigned.")

    # Annotation / description (20 pts)
    if has_annotation:
        score += 20
    else:
        reasons.append("No description annotation.")

    return MaturityResult(
        name=name,
        score=min(score, 100),
        grade=_grade(min(score, 100)),
        var_count=var_count,
        event_count=event_count,
        has_tags=has_tags,
        has_annotation=has_annotation,
        reasons=reasons,
    )
