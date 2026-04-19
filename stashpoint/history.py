"""History tracking for stash operations."""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

from stashpoint.storage import get_stash_path

HISTORY_FILE = "history.json"


def get_history_path() -> str:
    return os.path.join(os.path.dirname(get_stash_path()), HISTORY_FILE)


def load_history() -> List[Dict[str, Any]]:
    path = get_history_path()
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_history(history: List[Dict[str, Any]]) -> None:
    path = get_history_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)


def record_event(action: str, stash_name: str, variables: Dict[str, str] = None) -> None:
    history = load_history()
    entry = {
        "action": action,
        "stash": stash_name,
        "timestamp": datetime.utcnow().isoformat(),
        "variables": variables or {},
    }
    history.append(entry)
    save_history(history)


def get_stash_history(stash_name: str) -> List[Dict[str, Any]]:
    return [e for e in load_history() if e["stash"] == stash_name]


def clear_history() -> None:
    save_history([])
