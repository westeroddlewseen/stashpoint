"""Restore stash variables into the current environment by writing a shell-sourceable script.

This module provides functionality to restore a named stash into the current
shell session. Since a child process cannot modify its parent's environment,
restore works by writing an eval-able snippet to stdout or a temp file that
the shell can source.
"""

from __future__ import annotations

import os
import tempfile
from typing import Optional

from stashpoint.storage import load_stash
from stashpoint.export import export_bash, export_fish, export_powershell, export_dotenv
from stashpoint.lock import is_locked


class StashNotFoundError(Exception):
    """Raised when the requested stash does not exist."""


class StashLockedError(Exception):
    """Raised when attempting to restore a locked stash."""


class UnsupportedShellError(Exception):
    """Raised when the requested shell format is not supported."""


SUPPORTED_SHELLS = ("bash", "fish", "powershell", "dotenv")


def restore_stash(
    name: str,
    shell: str = "bash",
    prefix: Optional[str] = None,
    overwrite_existing: bool = True,
) -> str:
    """Return a shell-sourceable string that restores the named stash.

    Args:
        name: The name of the stash to restore.
        shell: Target shell format. One of 'bash', 'fish', 'powershell', 'dotenv'.
        prefix: Optional prefix to prepend to every variable name.
        overwrite_existing: If False, skip variables already set in the
            current process environment (bash/fish only; ignored for dotenv).

    Returns:
        A string of shell commands that can be eval'd or sourced.

    Raises:
        StashNotFoundError: If the stash does not exist.
        StashLockedError: If the stash is locked.
        UnsupportedShellError: If the shell argument is not recognised.
    """
    if shell not in SUPPORTED_SHELLS:
        raise UnsupportedShellError(
            f"Unsupported shell '{shell}'. Choose from: {', '.join(SUPPORTED_SHELLS)}"
        )

    if is_locked(name):
        raise StashLockedError(f"Stash '{name}' is locked and cannot be restored.")

    variables = load_stash(name)
    if variables is None:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    # Apply optional prefix
    if prefix:
        variables = {f"{prefix}{k}": v for k, v in variables.items()}

    # When overwrite_existing is False, filter out keys already in the env
    if not overwrite_existing and shell in ("bash", "fish"):
        variables = {
            k: v for k, v in variables.items() if k not in os.environ
        }

    exporters = {
        "bash": export_bash,
        "fish": export_fish,
        "powershell": export_powershell,
        "dotenv": export_dotenv,
    }
    return exporters[shell](variables)


def write_restore_script(
    name: str,
    shell: str = "bash",
    prefix: Optional[str] = None,
    overwrite_existing: bool = True,
    path: Optional[str] = None,
) -> str:
    """Write the restore snippet to a file and return its path.

    Useful for shells that require sourcing a file rather than eval-ing a
    string directly (e.g. ``source "$(stashpoint restore myenv)"`` patterns).

    Args:
        name: The name of the stash to restore.
        shell: Target shell format.
        prefix: Optional variable name prefix.
        overwrite_existing: Whether to overwrite already-set variables.
        path: Explicit file path to write to. If None, a temporary file is
            created and its path is returned.

    Returns:
        The absolute path to the written script file.
    """
    snippet = restore_stash(
        name,
        shell=shell,
        prefix=prefix,
        overwrite_existing=overwrite_existing,
    )

    if path is None:
        suffix = ".ps1" if shell == "powershell" else ".sh"
        fd, path = tempfile.mkstemp(suffix=suffix, prefix="stashpoint_")
        with os.fdopen(fd, "w") as fh:
            fh.write(snippet)
    else:
        with open(path, "w") as fh:
            fh.write(snippet)

    return path
