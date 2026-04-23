"""Tests for stashpoint.group module."""

import json
import pytest
from unittest.mock import patch, MagicMock
from stashpoint.group import (
    GroupNotFoundError,
    GroupAlreadyExistsError,
    create_group,
    delete_group,
    add_stash_to_group,
    remove_stash_from_group,
    get_group_members,
    list_groups,
    load_groups,
    save_groups,
)


@pytest.fixture
def mock_groups():
    data = {}

    def _load():
        return dict(data)

    def _save(groups):
        data.clear()
        data.update(groups)

    with patch("stashpoint.group.load_groups", side_effect=_load), \
         patch("stashpoint.group.save_groups", side_effect=_save):
        yield data


def test_create_group(mock_groups):
    create_group("staging")
    assert "staging" in mock_groups
    assert mock_groups["staging"] == []


def test_create_group_already_exists_raises(mock_groups):
    mock_groups["staging"] = []
    with pytest.raises(GroupAlreadyExistsError):
        create_group("staging")


def test_create_group_overwrite(mock_groups):
    mock_groups["staging"] = ["stash-a"]
    create_group("staging", overwrite=True)
    assert mock_groups["staging"] == []


def test_delete_group(mock_groups):
    mock_groups["staging"] = []
    delete_group("staging")
    assert "staging" not in mock_groups


def test_delete_group_not_found(mock_groups):
    with pytest.raises(GroupNotFoundError):
        delete_group("missing")


def test_add_stash_to_group(mock_groups):
    mock_groups["mygroup"] = []
    add_stash_to_group("mygroup", "stash-a")
    assert "stash-a" in mock_groups["mygroup"]


def test_add_stash_idempotent(mock_groups):
    mock_groups["mygroup"] = ["stash-a"]
    add_stash_to_group("mygroup", "stash-a")
    assert mock_groups["mygroup"].count("stash-a") == 1


def test_add_stash_group_not_found(mock_groups):
    with pytest.raises(GroupNotFoundError):
        add_stash_to_group("ghost", "stash-a")


def test_remove_stash_from_group(mock_groups):
    mock_groups["mygroup"] = ["stash-a", "stash-b"]
    remove_stash_from_group("mygroup", "stash-a")
    assert "stash-a" not in mock_groups["mygroup"]
    assert "stash-b" in mock_groups["mygroup"]


def test_get_group_members(mock_groups):
    mock_groups["mygroup"] = ["stash-a", "stash-b"]
    members = get_group_members("mygroup")
    assert members == ["stash-a", "stash-b"]


def test_get_group_members_not_found(mock_groups):
    with pytest.raises(GroupNotFoundError):
        get_group_members("nope")


def test_list_groups(mock_groups):
    mock_groups["beta"] = []
    mock_groups["alpha"] = []
    result = list_groups()
    assert result == ["alpha", "beta"]
