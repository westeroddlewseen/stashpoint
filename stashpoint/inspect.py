"""Inspect a stash: display metadata and variable summary."""

from datetime import datetime
from typing import Optional

from stashpoint.storage import load_stash
from stashpoint.lock import is_locked
from stashpoint.tag import get_tags
from stashpoint.history import get_stash_history


class StashNotFoundError(Exception):
    pass


def inspect_stash(name: str) -> dict:
    """Return a structured inspection report for a named stash."""
    variables = load_stash(name)
    if variables is None:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    tags = get_tags(name)
    locked = is_locked(name)
    history = get_stash_history(name)

    last_modified: Optional[str] = None
    if history:
        last_entry = history[-1]
        ts = last_entry.get("timestamp")
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                last_modified = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                last_modified = ts

    var_names = list(variables.keys())
    var_names.sort()

    return {
        "name": name,
        "variable_count": len(variables),
        "variables": var_names,
        "tags": sorted(tags),
        "locked": locked,
        "last_modified": last_modified,
        "history_entries": len(history),
    }


def format_inspect(report: dict) -> str:
    """Format an inspection report as a human-readable string."""
    lines = [
        f"Stash:          {report['name']}",
        f"Variables:      {report['variable_count']}",
        f"Locked:         {'yes' if report['locked'] else 'no'}",
        f"Tags:           {', '.join(report['tags']) if report['tags'] else '(none)'}",
        f"Last modified:  {report['last_modified'] or '(unknown)'}",
        f"History entries:{report['history_entries']}",
    ]
    if report["variables"]:
        lines.append("Variable names:")
        for var in report["variables"]:
            lines.append(f"  - {var}")
    return "\n".join(lines)
