"""Tests for stashpoint.clone."""

import pytest
from unittest.mock import patch

from stashpoint.clone import (
    clone_stash,
    get_clone_summary,
    StashNotFoundError,
    StashAlreadyExistsError,
)


SAMPLE_STASHES = {
    "dev": {"DB_HOST": "localhost", "DB_PORT": "5432"},
    "prod": {"DB_HOST": "prod.example.com", "DB_PORT": "5432"},
}


@pytest.fixture()
def mock_stashes(tmp_path):
    stashes = dict(SAMPLE_STASHES)
    with patch("stashpoint.clone.load_stashes", return_value=stashes), \
         patch("stashpoint.clone.save_stashes") as mock_save:
        yield stashes, mock_save


def test_clone_stash_creates_destination(mock_stashes):
    stashes, mock_save = mock_stashes
    result = clone_stash("dev", "dev-copy")
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert stashes["dev-copy"] == result
    mock_save.assert_called_once()


def test_clone_stash_is_independent(mock_stashes):
    stashes, _ = mock_stashes
    clone_stash("dev", "dev-copy")
    stashes["dev-copy"]["DB_HOST"] = "changed"
    assert stashes["dev"]["DB_HOST"] == "localhost"


def test_clone_stash_not_found(mock_stashes):
    with pytest.raises(StashNotFoundError, match="'missing'"):
        clone_stash("missing", "anywhere")


def test_clone_stash_destination_exists_no_overwrite(mock_stashes):
    with pytest.raises(StashAlreadyExistsError, match="'prod'"):
        clone_stash("dev", "prod", overwrite=False)


def test_clone_stash_destination_exists_with_overwrite(mock_stashes):
    stashes, _ = mock_stashes
    result = clone_stash("dev", "prod", overwrite=True)
    assert stashes["prod"] == result
    assert result["DB_HOST"] == "localhost"


def test_clone_stash_with_prefix(mock_stashes):
    stashes, _ = mock_stashes
    result = clone_stash("dev", "dev-prefixed", prefix="myapp")
    assert "MYAPP_DB_HOST" in result
    assert "MYAPP_DB_PORT" in result
    assert "DB_HOST" not in result


def test_clone_stash_prefix_not_duplicated(mock_stashes):
    """Variables already starting with the prefix should not get it twice."""
    stashes, _ = mock_stashes
    stashes["dev"]["MYAPP_ALREADY"] = "yes"
    result = clone_stash("dev", "dev-prefixed", prefix="myapp")
    assert "MYAPP_ALREADY" in result
    assert "MYAPP_MYAPP_ALREADY" not in result


def test_get_clone_summary_format():
    variables = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    summary = get_clone_summary("dev", "dev-copy", variables)
    assert "dev" in summary
    assert "dev-copy" in summary
    assert "2 variable(s)" in summary
    assert "DB_HOST" in summary
    assert "DB_PORT" in summary
