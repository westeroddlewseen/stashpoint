"""Compute a complexity score for a stash based on its structure and metadata."""

from dataclasses import dataclass
from typing import List

from stashpoint.storage import load_stashes
from stashpoint.tag import load_tags
from stashpoint.lock import is_locked
from stashpoint.dependency import load_dependencies


class StashNotFoundError(Exception):
    pass


@dataclass
class ComplexityResult:
    name: str
    score: int
    grade: str
    factors: List[str]


def _grade(score: int) -> str:
    if score >= 80:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def compute_complexity(name: str) -> ComplexityResult:
    """Compute a complexity score for the named stash.

    Score is built up from several contributing factors:
    - Number of variables (each contributes 2 points, capped at 40)
    - Number of tags (each contributes 5 points, capped at 20)
    - Whether the stash is locked (+10)
    - Number of declared dependencies (each contributes 10 points, capped at 30)
    """
    stashes = load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    variables = stashes[name]
    factors: List[str] = []
    score = 0

    # Variable count contribution
    var_points = min(len(variables) * 2, 40)
    if var_points:
        score += var_points
        factors.append(f"{len(variables)} variable(s) (+{var_points})")

    # Tag count contribution
    tags = load_tags().get(name, [])
    tag_points = min(len(tags) * 5, 20)
    if tag_points:
        score += tag_points
        factors.append(f"{len(tags)} tag(s) (+{tag_points})")

    # Lock contribution
    if is_locked(name):
        score += 10
        factors.append("locked (+10)")

    # Dependency contribution
    deps = load_dependencies().get(name, [])
    dep_points = min(len(deps) * 10, 30)
    if dep_points:
        score += dep_points
        factors.append(f"{len(deps)} dependency/ies (+{dep_points})")

    return ComplexityResult(
        name=name,
        score=score,
        grade=_grade(score),
        factors=factors,
    )
