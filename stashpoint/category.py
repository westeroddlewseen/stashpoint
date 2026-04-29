"""Category management for stashes."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashpoint.storage import load_stashes


class StashNotFoundError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class CategoryAlreadyExistsError(Exception):
    pass


def get_category_path() -> Path:
    from stashpoint.storage import get_stash_path
    return get_stash_path().parent / "categories.json"


def load_categories() -> Dict[str, List[str]]:
    """Return mapping of category name -> list of stash names."""
    path = get_category_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_categories(categories: Dict[str, List[str]]) -> None:
    path = get_category_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(categories, indent=2))


def create_category(name: str, overwrite: bool = False) -> None:
    categories = load_categories()
    if name in categories and not overwrite:
        raise CategoryAlreadyExistsError(f"Category '{name}' already exists.")
    categories[name] = categories.get(name, []) if not overwrite else []
    save_categories(categories)


def delete_category(name: str) -> None:
    categories = load_categories()
    if name not in categories:
        raise CategoryNotFoundError(f"Category '{name}' not found.")
    del categories[name]
    save_categories(categories)


def add_to_category(category: str, stash_name: str) -> None:
    stashes = load_stashes()
    if stash_name not in stashes:
        raise StashNotFoundError(f"Stash '{stash_name}' not found.")
    categories = load_categories()
    if category not in categories:
        raise CategoryNotFoundError(f"Category '{category}' not found.")
    if stash_name not in categories[category]:
        categories[category].append(stash_name)
    save_categories(categories)


def remove_from_category(category: str, stash_name: str) -> None:
    categories = load_categories()
    if category not in categories:
        raise CategoryNotFoundError(f"Category '{category}' not found.")
    if stash_name in categories[category]:
        categories[category].remove(stash_name)
    save_categories(categories)


def get_stash_categories(stash_name: str) -> List[str]:
    categories = load_categories()
    return sorted(cat for cat, members in categories.items() if stash_name in members)


def list_categories() -> List[str]:
    return sorted(load_categories().keys())
