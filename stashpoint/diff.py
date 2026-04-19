"""Diff functionality for comparing stashes."""
from typing import Dict, Tuple, List


def diff_stashes(
    stash_a: Dict[str, str],
    stash_b: Dict[str, str]
) -> Dict[str, Tuple[str, str]]:
    """
    Compare two stashes and return differences.

    Returns a dict of key -> (value_in_a, value_in_b) for all differing keys.
    Missing values are represented as None.
    """
    all_keys = set(stash_a.keys()) | set(stash_b.keys())
    diffs = {}
    for key in sorted(all_keys):
        val_a = stash_a.get(key)
        val_b = stash_b.get(key)
        if val_a != val_b:
            diffs[key] = (val_a, val_b)
    return diffs


def format_diff(diffs: Dict[str, Tuple[str, str]], name_a: str, name_b: str) -> List[str]:
    """
    Format diff results as human-readable lines.
    """
    if not diffs:
        return [f"No differences between '{name_a}' and '{name_b}'."]

    lines = [f"Diff: {name_a} -> {name_b}"]
    for key, (val_a, val_b) in diffs.items():
        if val_a is None:
            lines.append(f"  + {key}={val_b}")
        elif val_b is None:
            lines.append(f"  - {key}={val_a}")
        else:
            lines.append(f"  ~ {key}: {val_a!r} -> {val_b!r}")
    return lines
