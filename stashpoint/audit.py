"""Audit log for stash access and modification events."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

AUDIT_FILENAME = "audit.json"


def get_audit_path() -> Path:
    base = Path(os.environ.get("STASHPOINT_DIR", Path.home() / ".stashpoint"))
    base.mkdir(parents=True, exist_ok=True)
    return base / AUDIT_FILENAME


def load_audit(path: Optional[Path] = None) -> List[dict]:
    p = path or get_audit_path()
    if not p.exists():
        return []
    with open(p) as f:
        return json.load(f)


def save_audit(entries: List[dict], path: Optional[Path] = None) -> None:
    p = path or get_audit_path()
    with open(p, "w") as f:
        json.dump(entries, f, indent=2)


def record_audit(
    action: str,
    stash_name: str,
    detail: Optional[str] = None,
    path: Optional[Path] = None,
) -> dict:
    """Append an audit entry and return it."""
    entries = load_audit(path)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "stash": stash_name,
        "detail": detail,
    }
    entries.append(entry)
    save_audit(entries, path)
    return entry


def get_stash_audit(stash_name: str, path: Optional[Path] = None) -> List[dict]:
    """Return all audit entries for a specific stash."""
    return [e for e in load_audit(path) if e.get("stash") == stash_name]


def clear_audit(path: Optional[Path] = None) -> None:
    save_audit([], path)
