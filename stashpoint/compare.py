"""Compare multiple stashes side-by-side, showing all keys and their values."""

from typing import Dict, List, Optional, Tuple
from stashpoint.storage import load_stash


class StashNotFoundError(Exception):
    pass


def compare_stashes(names: List[str]) -> Dict[str, Dict[str, Optional[str]]]:
    """Load multiple stashes and return a unified key->stash->value mapping.

    Returns a dict where each key is an env var name and each value is a dict
    mapping stash name to its value (or None if the key is absent).
    """
    loaded: Dict[str, Dict[str, str]] = {}
    for name in names:
        stash = load_stash(name)
        if stash is None:
            raise StashNotFoundError(f"Stash '{name}' not found.")
        loaded[name] = stash

    all_keys: List[str] = sorted(
        {key for stash in loaded.values() for key in stash}
    )

    result: Dict[str, Dict[str, Optional[str]]] = {}
    for key in all_keys:
        result[key] = {name: loaded[name].get(key) for name in names}

    return result


def format_compare(
    comparison: Dict[str, Dict[str, Optional[str]]],
    names: List[str],
) -> str:
    """Format a comparison table as a human-readable string."""
    if not comparison:
        return "No variables found in any stash."

    col_width = max(len(n) for n in names)
    key_width = max((len(k) for k in comparison), default=3)
    key_width = max(key_width, 3)

    header = "  {key:<{kw}}  {cols}".format(
        key="KEY",
        kw=key_width,
        cols="  ".join(f"{n:<{col_width}}" for n in names),
    )
    separator = "-" * len(header)

    lines = [header, separator]
    for key, values in sorted(comparison.items()):
        row_values = []
        for name in names:
            val = values[name]
            cell = val if val is not None else "(absent)"
            row_values.append(f"{cell:<{col_width}}")
        lines.append(
            "  {key:<{kw}}  {cols}".format(
                key=key, kw=key_width, cols="  ".join(row_values)
            )
        )

    return "\n".join(lines)
