"""Tests for stashpoint.sentiment."""

from unittest.mock import patch

import pytest

from stashpoint.sentiment import (
    StashNotFoundError,
    SentimentIssue,
    SentimentResult,
    analyse_stash,
    format_sentiment,
)

MODULE = "stashpoint.sentiment.load_stashes"


def _mock(stashes):
    return patch(MODULE, return_value=stashes)


def test_stash_not_found_raises():
    with _mock({}):
        with pytest.raises(StashNotFoundError):
            analyse_stash("ghost")


def test_clean_stash_has_no_issues():
    stashes = {"myproject": {"DATABASE_HOST": "localhost", "PORT": "5432"}}
    with _mock(stashes):
        result = analyse_stash("myproject")
    assert result.issues == []


def test_clean_stash_scores_100():
    stashes = {"myproject": {"DATABASE_HOST": "localhost"}}
    with _mock(stashes):
        result = analyse_stash("myproject")
    assert result.score == 100


def test_secret_keyword_detected():
    stashes = {"s": {"API_TOKEN": "abc123"}}
    with _mock(stashes):
        result = analyse_stash("s")
    kinds = [i.kind for i in result.issues]
    assert "secret" in kinds


def test_deprecated_prefix_detected():
    stashes = {"s": {"OLD_ENDPOINT": "http://old.example.com"}}
    with _mock(stashes):
        result = analyse_stash("s")
    kinds = [i.kind for i in result.issues]
    assert "deprecated" in kinds


def test_terse_name_detected():
    stashes = {"s": {"DB": "postgres"}}
    with _mock(stashes):
        result = analyse_stash("s")
    kinds = [i.kind for i in result.issues]
    assert "terse" in kinds


def test_empty_value_detected():
    stashes = {"s": {"MY_VAR": ""}}
    with _mock(stashes):
        result = analyse_stash("s")
    kinds = [i.kind for i in result.issues]
    assert "empty_value" in kinds


def test_multiple_issues_on_same_var():
    # OLD_ prefix + empty value
    stashes = {"s": {"OLD_TOKEN": ""}}
    with _mock(stashes):
        result = analyse_stash("s")
    kinds = [i.kind for i in result.issues]
    assert "secret" in kinds
    assert "deprecated" in kinds
    assert "empty_value" in kinds


def test_score_decreases_with_issues():
    stashes = {"s": {"PASSWORD": "", "OLD_KEY": "x"}}
    with _mock(stashes):
        result = analyse_stash("s")
    assert result.score < 100


def test_score_never_below_zero():
    # Pile on lots of bad vars
    stashes = {"s": {f"OLD_TOKEN_{i}": "" for i in range(20)}}
    with _mock(stashes):
        result = analyse_stash("s")
    assert result.score >= 0


def test_format_sentiment_no_issues():
    result = SentimentResult(stash_name="clean")
    output = format_sentiment(result)
    assert "No issues found" in output
    assert "100/100" in output


def test_format_sentiment_with_issues():
    result = SentimentResult(
        stash_name="messy",
        issues=[
            SentimentIssue(variable="DB_PASSWORD", kind="secret", message="Looks sensitive."),
        ],
    )
    output = format_sentiment(result)
    assert "[SECRET]" in output
    assert "Looks sensitive." in output
