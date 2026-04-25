"""Quota management for stashpoint — limit the number of stashes or variables per stash."""

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_stashes


class QuotaExceededError(Exception):
    pass


def get_quota_path() -> Path:
    return get_stash_path().parent / "quota.json"


def load_quota() -> dict:
    path = get_quota_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def save_quota(quota: dict) -> None:
    path = get_quota_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(quota, f, indent=2)


def set_quota(max_stashes: Optional[int] = None, max_vars_per_stash: Optional[int] = None) -> dict:
    """Set global quota limits. Pass None to leave a limit unchanged."""
    quota = load_quota()
    if max_stashes is not None:
        if max_stashes < 1:
            raise ValueError("max_stashes must be at least 1")
        quota["max_stashes"] = max_stashes
    if max_vars_per_stash is not None:
        if max_vars_per_stash < 1:
            raise ValueError("max_vars_per_stash must be at least 1")
        quota["max_vars_per_stash"] = max_vars_per_stash
    save_quota(quota)
    return quota


def clear_quota() -> None:
    """Remove all quota limits."""
    save_quota({})


def check_stash_count() -> None:
    """Raise QuotaExceededError if adding a new stash would exceed the limit."""
    quota = load_quota()
    limit = quota.get("max_stashes")
    if limit is None:
        return
    stashes = load_stashes()
    if len(stashes) >= limit:
        raise QuotaExceededError(
            f"Stash quota exceeded: limit is {limit}, currently have {len(stashes)}."
        )


def check_var_count(variables: dict) -> None:
    """Raise QuotaExceededError if the variable count exceeds the per-stash limit."""
    quota = load_quota()
    limit = quota.get("max_vars_per_stash")
    if limit is None:
        return
    if len(variables) > limit:
        raise QuotaExceededError(
            f"Variable quota exceeded: limit is {limit} per stash, got {len(variables)}."
        )


def get_quota_status() -> dict:
    """Return current quota settings and usage."""
    quota = load_quota()
    stashes = load_stashes()
    return {
        "max_stashes": quota.get("max_stashes"),
        "current_stashes": len(stashes),
        "max_vars_per_stash": quota.get("max_vars_per_stash"),
    }
