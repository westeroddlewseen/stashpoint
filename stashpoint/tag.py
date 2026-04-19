import json
from pathlib import Path
from typing import Dict, List

from stashpoint.storage import get_stash_path


def get_tag_path() -> Path:
    return get_stash_path().parent / "tags.json"


def load_tags() -> Dict[str, List[str]]:
    path = get_tag_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_tags(tags: Dict[str, List[str]]) -> None:
    path = get_tag_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(tags, f, indent=2)


def add_tag(stash_name: str, tag: str) -> None:
    tags = load_tags()
    existing = tags.get(stash_name, [])
    if tag not in existing:
        existing.append(tag)
    tags[stash_name] = existing
    save_tags(tags)


def remove_tag(stash_name: str, tag: str) -> None:
    tags = load_tags()
    existing = tags.get(stash_name, [])
    tags[stash_name] = [t for t in existing if t != tag]
    save_tags(tags)


def get_tags(stash_name: str) -> List[str]:
    return load_tags().get(stash_name, [])


def find_by_tag(tag: str) -> List[str]:
    tags = load_tags()
    return sorted(name for name, tag_list in tags.items() if tag in tag_list)
