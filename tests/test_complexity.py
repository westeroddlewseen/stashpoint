"""Tests for stashpoint.complexity."""

import pytest
from unittest.mock import patch

from stashpoint.complexity import compute_complexity, StashNotFoundError


SAMPLE_STASHES = {
    "myproject": {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "SECRET_KEY": "abc123",
        "DEBUG": "true",
    },
    "empty": {},
}


@pytest.fixture()
def mock_deps():
    with patch("stashpoint.complexity.load_stashes", return_value=SAMPLE_STASHES), \
         patch("stashpoint.complexity.load_tags", return_value={}), \
         patch("stashpoint.complexity.is_locked", return_value=False), \
         patch("stashpoint.complexity.load_dependencies", return_value={}):
        yield


def test_stash_not_found_raises():
    with patch("stashpoint.complexity.load_stashes", return_value={}):
        with pytest.raises(StashNotFoundError):
            compute_complexity("missing")


def test_result_name(mock_deps):
    result = compute_complexity("myproject")
    assert result.name == "myproject"


def test_result_has_score(mock_deps):
    result = compute_complexity("myproject")
    assert isinstance(result.score, int)
    assert result.score >= 0


def test_result_has_grade(mock_deps):
    result = compute_complexity("myproject")
    assert result.grade in ("LOW", "MEDIUM", "HIGH")


def test_var_count_contributes_to_score():
    with patch("stashpoint.complexity.load_stashes", return_value=SAMPLE_STASHES), \
         patch("stashpoint.complexity.load_tags", return_value={}), \
         patch("stashpoint.complexity.is_locked", return_value=False), \
         patch("stashpoint.complexity.load_dependencies", return_value={}):
        result = compute_complexity("myproject")
        # 5 vars * 2 = 10 points from variables
        assert result.score >= 10


def test_empty_stash_scores_low():
    with patch("stashpoint.complexity.load_stashes", return_value=SAMPLE_STASHES), \
         patch("stashpoint.complexity.load_tags", return_value={}), \
         patch("stashpoint.complexity.is_locked", return_value=False), \
         patch("stashpoint.complexity.load_dependencies", return_value={}):
        result = compute_complexity("empty")
        assert result.grade == "LOW"
        assert result.score == 0


def test_lock_adds_to_score():
    with patch("stashpoint.complexity.load_stashes", return_value=SAMPLE_STASHES), \
         patch("stashpoint.complexity.load_tags", return_value={}), \
         patch("stashpoint.complexity.is_locked", return_value=True), \
         patch("stashpoint.complexity.load_dependencies", return_value={}):
        locked = compute_complexity("empty")
        assert locked.score == 10
        assert any("locked" in f for f in locked.factors)


def test_tags_add_to_score():
    with patch("stashpoint.complexity.load_stashes", return_value=SAMPLE_STASHES), \
         patch("stashpoint.complexity.load_tags", return_value={"empty": ["a", "b"]}), \
         patch("stashpoint.complexity.is_locked", return_value=False), \
         patch("stashpoint.complexity.load_dependencies", return_value={}):
        result = compute_complexity("empty")
        assert result.score == 10  # 2 tags * 5


def test_dependencies_add_to_score():
    with patch("stashpoint.complexity.load_stashes", return_value=SAMPLE_STASHES), \
         patch("stashpoint.complexity.load_tags", return_value={}), \
         patch("stashpoint.complexity.is_locked", return_value=False), \
         patch("stashpoint.complexity.load_dependencies", return_value={"empty": ["other"]}):
        result = compute_complexity("empty")
        assert result.score == 10  # 1 dep * 10


def test_high_complexity_grade():
    big_stash = {f"VAR_{i}": str(i) for i in range(25)}
    with patch("stashpoint.complexity.load_stashes", return_value={"big": big_stash}), \
         patch("stashpoint.complexity.load_tags", return_value={"big": ["t"] * 4}), \
         patch("stashpoint.complexity.is_locked", return_value=True), \
         patch("stashpoint.complexity.load_dependencies", return_value={"big": ["x", "y", "z"]}):
        result = compute_complexity("big")
        assert result.grade == "HIGH"
        assert result.score >= 80
