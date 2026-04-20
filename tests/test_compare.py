"""Tests for stashpoint.compare module."""

import pytest
from unittest.mock import patch
from stashpoint.compare import compare_stashes, format_compare, StashNotFoundError


SAMPLE_STASHES = {
    "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"},
    "prod": {"DB_HOST": "db.prod.example.com", "DB_PORT": "5432", "SECRET": "abc"},
    "staging": {"DB_HOST": "db.staging.example.com", "DEBUG": "false"},
}


def _mock_load(name):
    return SAMPLE_STASHES.get(name)


@patch("stashpoint.compare.load_stash", side_effect=_mock_load)
def test_compare_all_keys_present(mock_load):
    result = compare_stashes(["dev", "prod"])
    assert set(result.keys()) == {"DB_HOST", "DB_PORT", "DEBUG", "SECRET"}


@patch("stashpoint.compare.load_stash", side_effect=_mock_load)
def test_compare_absent_values_are_none(mock_load):
    result = compare_stashes(["dev", "prod"])
    assert result["SECRET"]["dev"] is None
    assert result["SECRET"]["prod"] == "abc"
    assert result["DEBUG"]["prod"] is None
    assert result["DEBUG"]["dev"] == "true"


@patch("stashpoint.compare.load_stash", side_effect=_mock_load)
def test_compare_shared_key_values(mock_load):
    result = compare_stashes(["dev", "prod"])
    assert result["DB_HOST"]["dev"] == "localhost"
    assert result["DB_HOST"]["prod"] == "db.prod.example.com"
    assert result["DB_PORT"]["dev"] == "5432"
    assert result["DB_PORT"]["prod"] == "5432"


@patch("stashpoint.compare.load_stash", return_value=None)
def test_compare_stash_not_found(mock_load):
    with pytest.raises(StashNotFoundError, match="'missing'"):
        compare_stashes(["missing"])


@patch("stashpoint.compare.load_stash", side_effect=_mock_load)
def test_compare_three_stashes(mock_load):
    result = compare_stashes(["dev", "prod", "staging"])
    assert result["DB_HOST"]["staging"] == "db.staging.example.com"
    assert result["SECRET"]["staging"] is None
    assert result["DB_PORT"]["staging"] is None


@patch("stashpoint.compare.load_stash", side_effect=_mock_load)
def test_format_compare_contains_headers(mock_load):
    comparison = compare_stashes(["dev", "prod"])
    output = format_compare(comparison, ["dev", "prod"])
    assert "dev" in output
    assert "prod" in output
    assert "KEY" in output


@patch("stashpoint.compare.load_stash", side_effect=_mock_load)
def test_format_compare_contains_absent(mock_load):
    comparison = compare_stashes(["dev", "prod"])
    output = format_compare(comparison, ["dev", "prod"])
    assert "(absent)" in output


@patch("stashpoint.compare.load_stash", side_effect=_mock_load)
def test_format_compare_contains_values(mock_load):
    comparison = compare_stashes(["dev", "prod"])
    output = format_compare(comparison, ["dev", "prod"])
    assert "localhost" in output
    assert "db.prod.example.com" in output


def test_format_compare_empty():
    output = format_compare({}, ["a", "b"])
    assert "No variables" in output
