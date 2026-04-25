"""Tests for stashpoint.score."""

from unittest.mock import patch

import pytest

from stashpoint.score import score_stash, rank_stashes, StashScore


_STASHES = {
    "dev": {"DB_URL": "postgres://localhost/dev", "DEBUG": "true"},
    "prod": {"DB_URL": "postgres://prod-host/app"},
    "empty": {},
}

_PINS = {"dev"}
_TAGS = {"dev": ["database", "local"], "prod": ["database"]}
_HISTORY = [
    {"stash": "dev", "action": "load"},
    {"stash": "dev", "action": "save"},
    {"stash": "prod", "action": "load"},
]


@pytest.fixture(autouse=True)
def mock_deps():
    with (
        patch("stashpoint.score.load_stashes", return_value=_STASHES),
        patch("stashpoint.score.load_pins", return_value=_PINS),
        patch("stashpoint.score.load_tags", return_value=_TAGS),
        patch("stashpoint.score.load_history", return_value=_HISTORY),
    ):
        yield


def test_score_stash_returns_dataclass():
    result = score_stash("dev")
    assert isinstance(result, StashScore)


def test_score_stash_name():
    result = score_stash("dev")
    assert result.name == "dev"


def test_score_stash_var_count():
    result = score_stash("dev")
    assert result.var_count == 2


def test_score_stash_event_count():
    result = score_stash("dev")
    assert result.event_count == 2


def test_score_stash_is_pinned_true():
    result = score_stash("dev")
    assert result.is_pinned is True


def test_score_stash_is_pinned_false():
    result = score_stash("prod")
    assert result.is_pinned is False


def test_score_stash_tag_count():
    result = score_stash("dev")
    assert result.tag_count == 2


def test_score_stash_numeric_score_positive():
    result = score_stash("dev")
    assert result.score > 0


def test_score_pinned_stash_higher_than_unpinned():
    dev = score_stash("dev")
    prod = score_stash("prod")
    assert dev.score > prod.score


def test_score_stash_not_found_raises():
    with pytest.raises(KeyError, match="unknown"):
        score_stash("unknown")


def test_rank_stashes_returns_list():
    result = rank_stashes()
    assert isinstance(result, list)
    assert len(result) == 3


def test_rank_stashes_sorted_descending():
    result = rank_stashes()
    scores = [r.score for r in result]
    assert scores == sorted(scores, reverse=True)


def test_rank_stashes_dev_is_first():
    result = rank_stashes()
    assert result[0].name == "dev"
