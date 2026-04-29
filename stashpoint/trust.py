"""Trust level management for stashes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

TRUST_LEVELS = ("untrusted", "low", "medium", "high", "verified")
DEFAULT_TRUST = "medium"


class StashNotFoundError(Exception):
    pass


class InvalidTrustLevelError(Exception):
    pass


def get_trust_path() -> Path:
    base = Path.home() / ".stashpoint"
    base.mkdir(parents=True, exist_ok=True)
    return base / "trust.json"


def load_trust() -> Dict[str, str]:
    path = get_trust_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def save_trust(data: Dict[str, str]) -> None:
    with get_trust_path().open("w") as f:
        json.dump(data, f, indent=2)


def set_trust(name: str, level: str, stashes: Optional[Dict] = None) -> str:
    """Set the trust level for a stash. Returns the assigned level."""
    if level not in TRUST_LEVELS:
        raise InvalidTrustLevelError(
            f"Invalid trust level '{level}'. Choose from: {', '.join(TRUST_LEVELS)}"
        )
    if stashes is not None and name not in stashes:
        raise StashNotFoundError(f"Stash '{name}' not found.")
    trust = load_trust()
    trust[name] = level
    save_trust(trust)
    return level


def get_trust(name: str) -> str:
    """Get the trust level for a stash, returning the default if unset."""
    trust = load_trust()
    return trust.get(name, DEFAULT_TRUST)


def remove_trust(name: str) -> bool:
    """Remove explicit trust level for a stash. Returns True if removed."""
    trust = load_trust()
    if name not in trust:
        return False
    del trust[name]
    save_trust(trust)
    return True


def list_trust() -> Dict[str, str]:
    """Return all explicitly set trust levels."""
    return load_trust()
