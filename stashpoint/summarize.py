"""Summarize a stash or all stashes with key statistics."""

from typing import Optional
from stashpoint.storage import load_stashes, load_stash
from stashpoint.tag import get_tags
from stashpoint.lock import is_locked
from stashpoint.pin import is_pinned


class StashNotFoundError(Exception):
    pass


def summarize_stash(name: str) -> dict:
    """Return a summary dict for a single named stash."""
    stashes = load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    variables = load_stash(name)
    tags = get_tags(name)
    locked = is_locked(name)
    pinned = is_pinned(name)

    empty_values = [k for k, v in variables.items() if v == ""]
    longest_key = max((k for k in variables), key=len, default="")
    longest_value = max((v for v in variables.values()), key=len, default="")

    return {
        "name": name,
        "var_count": len(variables),
        "tags": sorted(tags),
        "locked": locked,
        "pinned": pinned,
        "empty_values": empty_values,
        "longest_key": longest_key,
        "longest_value_length": len(longest_value),
    }


def summarize_all() -> list:
    """Return a list of summary dicts for all stashes, sorted by name."""
    stashes = load_stashes()
    results = []
    for name in sorted(stashes.keys()):
        try:
            results.append(summarize_stash(name))
        except StashNotFoundError:
            continue
    return results


def format_summary(summary: dict) -> str:
    """Format a single stash summary as a human-readable string."""
    lines = [
        f"Stash: {summary['name']}",
        f"  Variables : {summary['var_count']}",
        f"  Tags      : {', '.join(summary['tags']) if summary['tags'] else '(none)'}",
        f"  Locked    : {'yes' if summary['locked'] else 'no'}",
        f"  Pinned    : {'yes' if summary['pinned'] else 'no'}",
    ]
    if summary["empty_values"]:
        lines.append(f"  Empty vars: {', '.join(sorted(summary['empty_values']))}")
    if summary["longest_key"]:
        lines.append(f"  Longest key: {summary['longest_key']} ({len(summary['longest_key'])} chars)")
        lines.append(f"  Longest value: {summary['longest_value_length']} chars")
    return "\n".join(lines)
