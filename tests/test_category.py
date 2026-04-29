"""Tests for stashpoint.category."""

import pytest
from unittest.mock import patch

from stashpoint.category import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    StashNotFoundError,
    add_to_category,
    create_category,
    delete_category,
    get_stash_categories,
    list_categories,
    remove_from_category,
)


@pytest.fixture
def mock_categories():
    store = {}

    def _load():
        return dict(store)

    def _save(data):
        store.clear()
        store.update(data)

    with patch("stashpoint.category.load_categories", side_effect=_load), \
         patch("stashpoint.category.save_categories", side_effect=_save):
        yield store


@pytest.fixture
def mock_stashes():
    stashes = {"dev": {"FOO": "bar"}, "prod": {"FOO": "baz"}}
    with patch("stashpoint.category.load_stashes", return_value=stashes):
        yield stashes


def test_create_category(mock_categories):
    create_category("work")
    assert "work" in mock_categories


def test_create_category_already_exists_raises(mock_categories):
    create_category("work")
    with pytest.raises(CategoryAlreadyExistsError):
        create_category("work")


def test_create_category_overwrite(mock_categories, mock_stashes):
    create_category("work")
    add_to_category("work", "dev")
    create_category("work", overwrite=True)
    assert mock_categories["work"] == []


def test_delete_category(mock_categories):
    create_category("temp")
    delete_category("temp")
    assert "temp" not in mock_categories


def test_delete_category_not_found_raises(mock_categories):
    with pytest.raises(CategoryNotFoundError):
        delete_category("nonexistent")


def test_add_to_category(mock_categories, mock_stashes):
    create_category("group")
    add_to_category("group", "dev")
    assert "dev" in mock_categories["group"]


def test_add_to_category_stash_not_found(mock_categories, mock_stashes):
    create_category("group")
    with pytest.raises(StashNotFoundError):
        add_to_category("group", "ghost")


def test_add_to_category_idempotent(mock_categories, mock_stashes):
    create_category("group")
    add_to_category("group", "dev")
    add_to_category("group", "dev")
    assert mock_categories["group"].count("dev") == 1


def test_remove_from_category(mock_categories, mock_stashes):
    create_category("group")
    add_to_category("group", "dev")
    remove_from_category("group", "dev")
    assert "dev" not in mock_categories["group"]


def test_get_stash_categories(mock_categories, mock_stashes):
    create_category("alpha")
    create_category("beta")
    add_to_category("alpha", "dev")
    add_to_category("beta", "dev")
    cats = get_stash_categories("dev")
    assert cats == ["alpha", "beta"]


def test_list_categories_sorted(mock_categories):
    create_category("zebra")
    create_category("apple")
    assert list_categories() == ["apple", "zebra"]
