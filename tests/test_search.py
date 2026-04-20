"""Tests for stashpoint.search module."""

import pytest
from stashpoint.search import search_by_key, search_by_value, search_stashes


@pytest.fixture
def sample_stashes():
    return {
        "project-a": {
            "DATABASE_URL": "postgres://localhost/a",
            "API_KEY": "abc123",
            "DEBUG": "true",
        },
        "project-b": {
            "DATABASE_URL": "mysql://localhost/b",
            "API_SECRET": "xyz789",
            "PORT": "8080",
        },
        "staging": {
            "API_KEY": "stagingkey",
            "PORT": "443",
        },
    }


def test_search_by_key_exact(sample_stashes):
    results = search_by_key("API_KEY", sample_stashes)
    assert len(results) == 2
    stash_names = {r[0] for r in results}
    assert stash_names == {"project-a", "staging"}


def test_search_by_key_glob(sample_stashes):
    results = search_by_key("API_*", sample_stashes)
    keys = {(r[0], r[1]) for r in results}
    assert ("project-a", "API_KEY") in keys
    assert ("project-b", "API_SECRET") in keys
    assert ("staging", "API_KEY") in keys


def test_search_by_key_no_match(sample_stashes):
    results = search_by_key("NONEXISTENT", sample_stashes)
    assert results == []


def test_search_by_value_glob(sample_stashes):
    results = search_by_value("*localhost*", sample_stashes)
    assert len(results) == 2
    keys = {r[1] for r in results}
    assert keys == {"DATABASE_URL"}


def test_search_by_value_exact(sample_stashes):
    results = search_by_value("true", sample_stashes)
    assert len(results) == 1
    assert results[0] == ("project-a", "DEBUG", "true")


def test_search_by_value_no_match(sample_stashes):
    results = search_by_value("nomatch", sample_stashes)
    assert results == []


def test_search_stashes_both_patterns(sample_stashes):
    results = search_stashes(key_pattern="DATABASE_URL", value_pattern="postgres*", stashes=sample_stashes)
    assert len(results) == 1
    assert results[0][0] == "project-a"


def test_search_stashes_key_only(sample_stashes):
    results = search_stashes(key_pattern="PORT", stashes=sample_stashes)
    stash_names = {r[0] for r in results}
    assert stash_names == {"project-b", "staging"}


def test_search_stashes_value_only(sample_stashes):
    results = search_stashes(value_pattern="8080", stashes=sample_stashes)
    assert len(results) == 1
    assert results[0] == ("project-b", "PORT", "8080")


def test_search_stashes_no_patterns_raises(sample_stashes):
    with pytest.raises(ValueError, match="At least one"):
        search_stashes(stashes=sample_stashes)


def test_search_results_are_sorted(sample_stashes):
    results = search_by_key("*", sample_stashes)
    assert results == sorted(results)
