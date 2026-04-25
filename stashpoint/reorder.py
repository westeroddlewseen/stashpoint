"""Reorder (sort or manually arrange) variables within a stash."""

from typing import List, Optional
from stashpoint.storage import load_stash, save_stash


class StashNotFoundError(Exception):
    pass


class InvalidKeyError(Exception):
    pass


def reorder_stash(
    name: str,
    order: Optional[List[str]] = None,
    sort: bool = False,
    reverse: bool = False,
) -> dict:
    """Reorder variables in a stash.

    Args:
        name: The stash name.
        order: Explicit list of keys defining the desired order. Keys not
               listed are appended at the end in their original relative order.
        sort: If True, sort keys alphabetically (ignored when order is given).
        reverse: If True, reverse the final ordering.

    Returns:
        The reordered stash dict.

    Raises:
        StashNotFoundError: If the stash does not exist.
        InvalidKeyError: If any key in *order* is not present in the stash.
    """
    stash = load_stash(name)
    if stash is None:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    if order is not None:
        unknown = [k for k in order if k not in stash]
        if unknown:
            raise InvalidKeyError(
                f"Keys not found in stash '{name}': {', '.join(unknown)}"
            )
        # Keys explicitly listed come first; remaining keys follow in original order.
        remaining = [k for k in stash if k not in order]
        final_order = list(order) + remaining
    elif sort:
        final_order = sorted(stash.keys())
    else:
        final_order = list(stash.keys())

    if reverse:
        final_order = list(reversed(final_order))

    reordered = {k: stash[k] for k in final_order}
    save_stash(name, reordered)
    return reordered


def get_reorder_summary(original: dict, reordered: dict) -> List[str]:
    """Return a list of strings describing the position changes."""
    orig_keys = list(original.keys())
    new_keys = list(reordered.keys())
    lines = []
    for new_idx, key in enumerate(new_keys):
        old_idx = orig_keys.index(key)
        if old_idx != new_idx:
            lines.append(f"  {key}: position {old_idx + 1} -> {new_idx + 1}")
    return lines
