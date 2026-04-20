"""Snapshot support: capture current environment variables into a stash."""

import os
from typing import Dict, List, Optional

from stashpoint.storage import save_stash, load_stash


class StashAlreadyExistsError(Exception):
    pass


def capture_env(prefix: Optional[str] = None) -> Dict[str, str]:
    """Return current environment variables, optionally filtered by prefix."""
    env = dict(os.environ)
    if prefix:
        env = {k: v for k, v in env.items() if k.startswith(prefix)}
    return env


def snapshot(
    name: str,
    prefix: Optional[str] = None,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Capture environment variables and save them as a named stash.

    Args:
        name: The stash name to save under.
        prefix: If provided, only capture variables whose names start with this.
        keys: If provided, only capture these specific variable names.
        overwrite: If False and the stash already exists, raise StashAlreadyExistsError.

    Returns:
        The dict of captured variables that were saved.
    """
    if not overwrite:
        existing = load_stash(name)
        if existing is not None:
            raise StashAlreadyExistsError(
                f"Stash '{name}' already exists. Use --overwrite to replace it."
            )

    variables = capture_env(prefix=prefix)

    if keys:
        variables = {k: variables[k] for k in keys if k in variables}

    save_stash(name, variables)
    return variables
