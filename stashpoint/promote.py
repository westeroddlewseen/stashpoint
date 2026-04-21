"""Promote a stash by copying its variables into the current environment (shell export helper)."""

from stashpoint.storage import load_stash
from stashpoint.export import export_variables


class StashNotFoundError(Exception):
    pass


class UnsupportedShellError(Exception):
    pass


SUPPORTED_SHELLS = ("bash", "fish", "powershell", "dotenv")


def promote_stash(name: str, shell: str, prefix: str = "", keys: list[str] | None = None) -> str:
    """Return shell-specific export commands for the named stash.

    Args:
        name:   The stash name to promote.
        shell:  Target shell format ('bash', 'fish', 'powershell', 'dotenv').
        prefix: Optional prefix to prepend to every variable name.
        keys:   If provided, only include these keys.

    Returns:
        A string of shell commands ready to be eval'd / sourced.

    Raises:
        StashNotFoundError: If the stash does not exist.
        UnsupportedShellError: If the shell format is not supported.
    """
    if shell not in SUPPORTED_SHELLS:
        raise UnsupportedShellError(
            f"Unsupported shell '{shell}'. Choose from: {', '.join(SUPPORTED_SHELLS)}"
        )

    variables = load_stash(name)
    if variables is None:
        raise StashNotFoundError(f"Stash '{name}' not found.")

    if keys:
        variables = {k: v for k, v in variables.items() if k in keys}

    if prefix:
        variables = {f"{prefix}{k}": v for k, v in variables.items()}

    return export_variables(variables, shell)
