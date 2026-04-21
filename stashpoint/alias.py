"""Alias support: map short names to existing stashes."""

import json
from pathlib import Path
from stashpoint.storage import get_stash_path


class AliasNotFoundError(Exception):
    pass


class AliasAlreadyExistsError(Exception):
    pass


class AliasTargetNotFoundError(Exception):
    pass


def get_alias_path() -> Path:
    return get_stash_path().parent / "aliases.json"


def load_aliases() -> dict:
    path = get_alias_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_aliases(aliases: dict) -> None:
    path = get_alias_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(aliases, f, indent=2)


def add_alias(alias: str, target: str, overwrite: bool = False) -> None:
    """Create an alias pointing to target stash."""
    from stashpoint.storage import load_stashes
    stashes = load_stashes()
    if target not in stashes:
        raise AliasTargetNotFoundError(f"Stash '{target}' does not exist.")
    aliases = load_aliases()
    if alias in aliases and not overwrite:
        raise AliasAlreadyExistsError(f"Alias '{alias}' already exists.")
    aliases[alias] = target
    save_aliases(aliases)


def remove_alias(alias: str) -> None:
    """Remove an existing alias."""
    aliases = load_aliases()
    if alias not in aliases:
        raise AliasNotFoundError(f"Alias '{alias}' not found.")
    del aliases[alias]
    save_aliases(aliases)


def resolve_alias(alias: str) -> str:
    """Return the stash name an alias points to."""
    aliases = load_aliases()
    if alias not in aliases:
        raise AliasNotFoundError(f"Alias '{alias}' not found.")
    return aliases[alias]


def list_aliases() -> dict:
    """Return all alias -> target mappings."""
    return load_aliases()
