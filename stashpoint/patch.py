"""Apply partial updates (patches) to an existing stash."""

from stashpoint.storage import load_stash, save_stash, load_stashes


class StashNotFoundError(Exception):
    pass


class InvalidPatchError(Exception):
    pass


def patch_stash(name: str, updates: dict, remove_keys: list = None) -> dict:
    """Apply a patch to an existing stash.

    Args:
        name: The name of the stash to patch.
        updates: A dict of key/value pairs to set or update.
        remove_keys: A list of keys to remove from the stash.

    Returns:
        The updated stash variables dict.

    Raises:
        StashNotFoundError: If the named stash does not exist.
        InvalidPatchError: If updates and remove_keys are both empty.
    """
    if not updates and not remove_keys:
        raise InvalidPatchError("Patch must include at least one update or removal.")

    stashes = load_stashes()
    if name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    variables = dict(stashes[name])

    if updates:
        variables.update(updates)

    if remove_keys:
        for key in remove_keys:
            variables.pop(key, None)

    save_stash(name, variables)
    return variables


def get_patch_summary(original: dict, updated: dict) -> dict:
    """Return a summary of changes between two variable dicts.

    Returns a dict with keys 'added', 'modified', and 'removed'.
    """
    added = {k: v for k, v in updated.items() if k not in original}
    removed = {k: original[k] for k in original if k not in updated}
    modified = {
        k: {"old": original[k], "new": updated[k]}
        for k in original
        if k in updated and original[k] != updated[k]
    }
    return {"added": added, "modified": modified, "removed": removed}
