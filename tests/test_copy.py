"""Tests for stashpoint copy/rename functionality."""

import pytest
from unittest.mock import patch

from stashpoint.copy import copy_stash, rename_stash, StashNotFoundError, StashAlreadyExistsError


SAMPLE_STASHES = {
    "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
    "prod": {"DB_HOST": "db.prod.example.com", "DEBUG": "false"},
}


@pytest.fixture
def mock_stashes():
    stashes = dict(SAMPLE_STASHES)
    with patch("stashpoint.copy.load_stashes", return_value=stashes), \
         patch("stashpoint.copy.save_stashes") as mock_save:
        yield stashes, mock_save


def test_copy_stash(mock_stashes):
    stashes, mock_save = mock_stashes
    result = copy_stash("dev", "dev-backup")
    assert result == SAMPLE_STASHES["dev"]
    assert stashes["dev-backup"] == SAMPLE_STASHES["dev"]
    mock_save.assert_called_once_with(stashes)


def test_copy_stash_is_independent(mock_stashes):
    stashes, _ = mock_stashes
    copy_stash("dev", "dev-backup")
    stashes["dev"]["NEW_VAR"] = "value"
    assert "NEW_VAR" not in stashes["dev-backup"]


def test_copy_stash_not_found(mock_stashes):
    with pytest.raises(StashNotFoundError):
        copy_stash("nonexistent", "target")


def test_copy_stash_destination_exists_no_overwrite(mock_stashes):
    with pytest.raises(StashAlreadyExistsError):
        copy_stash("dev", "prod")


def test_copy_stash_destination_exists_with_overwrite(mock_stashes):
    stashes, mock_save = mock_stashes
    result = copy_stash("dev", "prod", overwrite=True)
    assert result == SAMPLE_STASHES["dev"]
    mock_save.assert_called_once()


def test_rename_stash(mock_stashes):
    stashes, mock_save = mock_stashes
    result = rename_stash("dev", "development")
    assert result == SAMPLE_STASHES["dev"]
    assert "development" in stashes
    assert "dev" not in stashes
    mock_save.assert_called_once_with(stashes)


def test_rename_stash_not_found(mock_stashes):
    with pytest.raises(StashNotFoundError):
        rename_stash("nonexistent", "target")


def test_rename_stash_destination_exists_no_overwrite(mock_stashes):
    with pytest.raises(StashAlreadyExistsError):
        rename_stash("dev", "prod")


def test_rename_stash_destination_exists_with_overwrite(mock_stashes):
    stashes, mock_save = mock_stashes
    result = rename_stash("dev", "prod", overwrite=True)
    assert result == SAMPLE_STASHES["dev"]
    assert "dev" not in stashes
    mock_save.assert_called_once()
