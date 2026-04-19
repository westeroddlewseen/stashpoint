"""Merge functionality for combining stashes."""

from typing import Dict, Optional


class StashNotFoundError(Exception):
    pass


def merge_stashes(
    stashes: Dict[str, Dict[str, str]],
    source: str,
    target: str,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Merge variables from source stash into target stash.

    Args:
        stashes: All existing stashes.
        source: Name of the stash to merge from.
        target: Name of the stash to merge into.
        overwrite: If True, source values overwrite target values on conflict.

    Returns:
        The merged variable dict (not yet saved).

    Raises:
        StashNotFoundError: If source or target stash does not exist.
    """
    if source not in stashes:
        raise StashNotFoundError(f"Stash '{source}' not found.")
    if target not in stashes:
        raise StashNotFoundError(f"Stash '{target}' not found.")

    target_vars = dict(stashes[target])
    source_vars = stashes[source]

    for key, value in source_vars.items():
        if key not in target_vars or overwrite:
            target_vars[key] = value

    return target_vars


def get_conflicts(
    stashes: Dict[str, Dict[str, str]],
    source: str,
    target: str,
) -> Dict[str, tuple]:
    """Return keys that exist in both stashes with different values.

    Returns:
        Dict mapping conflicting key -> (target_value, source_value).
    """
    if source not in stashes or target not in stashes:
        return {}

    conflicts = {}
    for key, value in stashes[source].items():
        if key in stashes[target] and stashes[target][key] != value:
            conflicts[key] = (stashes[target][key], value)
    return conflicts
