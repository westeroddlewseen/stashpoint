"""Tests for stashpoint.maturity."""

import pytest
from unittest.mock import patch

from stashpoint.maturity import compute_maturity, StashNotFoundError


STASHES = {
    "full": {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
    "sparse": {"X": "1"},
    "empty": {},
}

HISTORY_FULL = [{"event": "load"} for _ in range(12)]
HISTORY_SPARSE = [{"event": "load"}]
HISTORY_EMPTY = []


def _mock(stashes, history, tags=None, annotation=None):
    """Return a context manager stack that patches all external deps."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with patch("stashpoint.maturity.load_stashes", return_value=stashes), \
             patch("stashpoint.maturity.get_stash_history", return_value=history), \
             patch("stashpoint.maturity.load_tags", return_value={}), \
             patch("stashpoint.maturity.get_tags", return_value=tags or []), \
             patch("stashpoint.maturity.load_annotations", return_value={}), \
             patch("stashpoint.maturity.get_annotation", return_value=annotation):
            yield

    return _ctx()


def test_stash_not_found_raises():
    with _mock({}, []):
        with pytest.raises(StashNotFoundError):
            compute_maturity("missing")


def test_result_name():
    with _mock(STASHES, HISTORY_FULL, tags=["prod"], annotation="My stash"):
        result = compute_maturity("full")
    assert result.name == "full"


def test_full_stash_scores_high():
    with _mock(STASHES, HISTORY_FULL, tags=["prod"], annotation="desc"):
        result = compute_maturity("full")
    assert result.score == 100
    assert result.grade == "A"


def test_empty_stash_scores_low():
    with _mock(STASHES, HISTORY_EMPTY):
        result = compute_maturity("empty")
    assert result.score < 35
    assert result.grade == "F"


def test_no_tags_adds_reason():
    with _mock(STASHES, HISTORY_FULL, tags=[], annotation="desc"):
        result = compute_maturity("full")
    assert any("tag" in r.lower() for r in result.reasons)


def test_no_annotation_adds_reason():
    with _mock(STASHES, HISTORY_FULL, tags=["t"], annotation=None):
        result = compute_maturity("full")
    assert any("description" in r.lower() or "annotation" in r.lower() for r in result.reasons)


def test_var_count_reflected():
    with _mock(STASHES, HISTORY_EMPTY):
        result = compute_maturity("sparse")
    assert result.var_count == 1


def test_event_count_reflected():
    with _mock(STASHES, HISTORY_SPARSE):
        result = compute_maturity("sparse")
    assert result.event_count == 1


def test_grade_b_range():
    # 5 vars (40) + 10 events (30) + no tags (0) + annotation (20) = 90 -> A
    # Tweak: 5 vars (40) + 3 events (9) + tags (10) + annotation (20) = 79 -> B
    with _mock(STASHES, [{"e": "x"} for _ in range(3)], tags=["t"], annotation="desc"):
        result = compute_maturity("full")
    assert result.grade == "B"
    assert result.score == 79


def test_has_tags_and_annotation_flags():
    with _mock(STASHES, HISTORY_FULL, tags=["env"], annotation="something"):
        result = compute_maturity("full")
    assert result.has_tags is True
    assert result.has_annotation is True


def test_score_capped_at_100():
    with _mock(STASHES, HISTORY_FULL * 5, tags=["t", "u"], annotation="x"):
        result = compute_maturity("full")
    assert result.score <= 100
