"""Search stashes by key or value patterns."""

import fnmatch
from typing import Dict, List, Tuple

from stashpoint.storage import load_stashes


def search_by_key(pattern: str, stashes: Dict[str, Dict[str, str]] = None) -> List[Tuple[str, str, str]]:
    """Find stash entries where a key matches the given glob pattern.

    Returns a list of (stash_name, key, value) tuples.
    """
    if stashes is None:
        stashes = load_stashes()

    results = []
    for stash_name, variables in stashes.items():
        for key, value in variables.items():
            if fnmatch.fnmatch(key, pattern):
                results.append((stash_name, key, value))
    return sorted(results)


def search_by_value(pattern: str, stashes: Dict[str, Dict[str, str]] = None) -> List[Tuple[str, str, str]]:
    """Find stash entries where a value matches the given glob pattern.

    Returns a list of (stash_name, key, value) tuples.
    """
    if stashes is None:
        stashes = load_stashes()

    results = []
    for stash_name, variables in stashes.items():
        for key, value in variables.items():
            if fnmatch.fnmatch(value, pattern):
                results.append((stash_name, key, value))
    return sorted(results)


def search_stashes(key_pattern: str = None, value_pattern: str = None, stashes: Dict[str, Dict[str, str]] = None) -> List[Tuple[str, str, str]]:
    """Search stashes by key and/or value pattern.

    At least one of key_pattern or value_pattern must be provided.
    When both are given, both must match.
    Returns a list of (stash_name, key, value) tuples.
    """
    if key_pattern is None and value_pattern is None:
        raise ValueError("At least one of key_pattern or value_pattern must be provided.")

    if stashes is None:
        stashes = load_stashes()

    results = []
    for stash_name, variables in stashes.items():
        for key, value in variables.items():
            key_match = fnmatch.fnmatch(key, key_pattern) if key_pattern else True
            value_match = fnmatch.fnmatch(value, value_pattern) if value_pattern else True
            if key_match and value_match:
                results.append((stash_name, key, value))
    return sorted(results)
