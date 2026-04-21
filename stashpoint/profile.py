"""Profile support: group multiple stashes under a named profile."""

import json
from pathlib import Path
from typing import Dict, List

from stashpoint.storage import get_stash_path


class ProfileNotFoundError(Exception):
    pass


class ProfileAlreadyExistsError(Exception):
    pass


def get_profile_path() -> Path:
    return get_stash_path().parent / "profiles.json"


def load_profiles() -> Dict[str, List[str]]:
    path = get_profile_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_profiles(profiles: Dict[str, List[str]]) -> None:
    path = get_profile_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(profiles, f, indent=2)


def create_profile(name: str, stashes: List[str], overwrite: bool = False) -> None:
    profiles = load_profiles()
    if name in profiles and not overwrite:
        raise ProfileAlreadyExistsError(f"Profile '{name}' already exists.")
    profiles[name] = list(stashes)
    save_profiles(profiles)


def delete_profile(name: str) -> None:
    profiles = load_profiles()
    if name not in profiles:
        raise ProfileNotFoundError(f"Profile '{name}' not found.")
    del profiles[name]
    save_profiles(profiles)


def get_profile(name: str) -> List[str]:
    profiles = load_profiles()
    if name not in profiles:
        raise ProfileNotFoundError(f"Profile '{name}' not found.")
    return list(profiles[name])


def add_stash_to_profile(profile_name: str, stash_name: str) -> None:
    profiles = load_profiles()
    if profile_name not in profiles:
        raise ProfileNotFoundError(f"Profile '{profile_name}' not found.")
    if stash_name not in profiles[profile_name]:
        profiles[profile_name].append(stash_name)
        save_profiles(profiles)


def remove_stash_from_profile(profile_name: str, stash_name: str) -> None:
    profiles = load_profiles()
    if profile_name not in profiles:
        raise ProfileNotFoundError(f"Profile '{profile_name}' not found.")
    if stash_name in profiles[profile_name]:
        profiles[profile_name].remove(stash_name)
        save_profiles(profiles)
