"""Clone a stash into a new project-scoped namespace."""

from stashpoint.storage import load_stashes, save_stashes


class StashNotFoundError(Exception):
    """Raised when the source stash does not exist."""


class StashAlreadyExistsError(Exception):
    """Raised when the destination stash already exists and overwrite is False."""


def clone_stash(
    source: str,
    destination: str,
    prefix: str | None = None,
    overwrite: bool = False,
) -> dict:
    """Clone *source* into *destination*, optionally scoping variable names with *prefix*.

    Parameters
    ----------
    source:
        Name of the stash to clone.
    destination:
        Name for the new stash.
    prefix:
        If given, every variable name in the cloned stash is prefixed with
        ``<PREFIX>_`` (uppercased).  Variables that already start with the
        prefix are left unchanged.
    overwrite:
        When *True* an existing stash named *destination* is replaced.

    Returns
    -------
    dict
        The variables stored in the new stash.
    """
    stashes = load_stashes()

    if source not in stashes:
        raise StashNotFoundError(f"Stash '{source}' not found.")

    if destination in stashes and not overwrite:
        raise StashAlreadyExistsError(
            f"Stash '{destination}' already exists. Use overwrite=True to replace it."
        )

    variables: dict = dict(stashes[source])

    if prefix:
        upper_prefix = prefix.upper() + "_"
        variables = {
            (k if k.startswith(upper_prefix) else upper_prefix + k): v
            for k, v in variables.items()
        }

    stashes[destination] = variables
    save_stashes(stashes)
    return variables


def get_clone_summary(source: str, destination: str, variables: dict) -> str:
    """Return a human-readable summary of a clone operation."""
    lines = [
        f"Cloned '{source}' → '{destination}' ({len(variables)} variable(s))",
    ]
    for key in sorted(variables):
        lines.append(f"  {key}")
    return "\n".join(lines)
