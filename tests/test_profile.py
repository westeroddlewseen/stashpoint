"""Tests for stashpoint.profile module."""

import json
import pytest
from unittest.mock import patch

from stashpoint.profile import (
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    add_stash_to_profile,
    create_profile,
    delete_profile,
    get_profile,
    load_profiles,
    remove_stash_from_profile,
    save_profiles,
)


@pytest.fixture
def mock_profiles(tmp_path, monkeypatch):
    profile_file = tmp_path / "profiles.json"
    monkeypatch.setattr("stashpoint.profile.get_profile_path", lambda: profile_file)
    return profile_file


def test_load_profiles_empty(mock_profiles):
    result = load_profiles()
    assert result == {}


def test_create_and_get_profile(mock_profiles):
    create_profile("dev", ["base", "secrets"])
    result = get_profile("dev")
    assert result == ["base", "secrets"]


def test_create_profile_overwrite(mock_profiles):
    create_profile("dev", ["base"])
    create_profile("dev", ["other"], overwrite=True)
    assert get_profile("dev") == ["other"]


def test_create_profile_no_overwrite_raises(mock_profiles):
    create_profile("dev", ["base"])
    with pytest.raises(ProfileAlreadyExistsError):
        create_profile("dev", ["other"])


def test_get_profile_not_found(mock_profiles):
    with pytest.raises(ProfileNotFoundError):
        get_profile("nonexistent")


def test_delete_profile(mock_profiles):
    create_profile("dev", ["base"])
    delete_profile("dev")
    profiles = load_profiles()
    assert "dev" not in profiles


def test_delete_profile_not_found(mock_profiles):
    with pytest.raises(ProfileNotFoundError):
        delete_profile("ghost")


def test_add_stash_to_profile(mock_profiles):
    create_profile("dev", ["base"])
    add_stash_to_profile("dev", "extra")
    assert "extra" in get_profile("dev")


def test_add_stash_idempotent(mock_profiles):
    create_profile("dev", ["base"])
    add_stash_to_profile("dev", "base")
    assert get_profile("dev").count("base") == 1


def test_add_stash_profile_not_found(mock_profiles):
    with pytest.raises(ProfileNotFoundError):
        add_stash_to_profile("ghost", "base")


def test_remove_stash_from_profile(mock_profiles):
    create_profile("dev", ["base", "extra"])
    remove_stash_from_profile("dev", "extra")
    assert "extra" not in get_profile("dev")


def test_remove_stash_profile_not_found(mock_profiles):
    with pytest.raises(ProfileNotFoundError):
        remove_stash_from_profile("ghost", "base")


def test_get_profile_returns_copy(mock_profiles):
    create_profile("dev", ["base"])
    result = get_profile("dev")
    result.append("injected")
    assert "injected" not in get_profile("dev")
