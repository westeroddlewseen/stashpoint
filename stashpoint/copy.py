"""Copy/rename stash functionality for stashpoint."""

from stashpoint.storage import load_stashes, save_stashes


class StashNotFoundError(Exception):
    pass


class StashAlreadyExistsError(Exception):
    pass


def copy_stash(source: str, destination: str, overwrite: bool = False) -> dict:
    """Copy a stash to a new name.

    Args:
        source: Name of the stash to copy.
        destination: Name for the new stash.
        overwrite: If True, overwrite destination if it exists.

    Returns:
        The copied stash variables dict.

    Raises:
        StashNotFoundError: If source stash does not exist.
        StashAlreadyExistsError: If destination exists and overwrite is False.
    """
    stashes = load_stashes()

    if source not in stashes:
        raise StashNotFoundError(f"Stash '{source}' not found.")

    if destination in stashes and not overwrite:
        raise StashAlreadyExistsError(
            f"Stash '{destination}' already exists. Use --overwrite to replace it."
        )

    stashes[destination] = dict(stashes[source])
    save_stashes(stashes)
    return stashes[destination]


def rename_stash(source: str, destination: str, overwrite: bool = False) -> dict:
    """Rename a stash.

    Args:
        source: Name of the stash to rename.
        destination: New name for the stash.
        overwrite: If True, overwrite destination if it exists.

    Returns:
        The renamed stash variables dict.

    Raises:
        StashNotFoundError: If source stash does not exist.
        StashAlreadyExistsError: If destination exists and overwrite is False.
    """
    stashes = load_stashes()

    if source not in stashes:
        raise StashNotFoundError(f"Stash '{source}' not found.")

    if destination in stashes and not overwrite:
        raise StashAlreadyExistsError(
            f"Stash '{destination}' already exists. Use --overwrite to replace it."
        )

    stashes[destination] = stashes.pop(source)
    save_stashes(stashes)
    return stashes[destination]
