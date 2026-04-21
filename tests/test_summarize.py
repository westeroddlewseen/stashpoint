"""Tests for stashpoint.summarize."""

import pytest
from unittest.mock import patch
from stashpoint.summarize import summarize_stash, summarize_all, format_summary, StashNotFoundError


STASHES = {
    "prod": {"DB_HOST": "db.prod.example.com", "API_KEY": "secret", "DEBUG": ""},
    "dev": {"DB_HOST": "localhost"},
}


@pytest.fixture(autouse=True)
def mock_deps(monkeypatch):
    monkeypatch.setattr("stashpoint.summarize.load_stashes", lambda: STASHES)
    monkeypatch.setattr("stashpoint.summarize.load_stash", lambda name: STASHES[name])
    monkeypatch.setattr("stashpoint.summarize.get_tags", lambda name: ["web", "infra"] if name == "prod" else [])
    monkeypatch.setattr("stashpoint.summarize.is_locked", lambda name: name == "prod")
    monkeypatch.setattr("stashpoint.summarize.is_pinned", lambda name: False)


def test_summarize_stash_name():
    result = summarize_stash("prod")
    assert result["name"] == "prod"


def test_summarize_stash_var_count():
    result = summarize_stash("prod")
    assert result["var_count"] == 3


def test_summarize_stash_tags_sorted():
    result = summarize_stash("prod")
    assert result["tags"] == ["infra", "web"]


def test_summarize_stash_locked():
    assert summarize_stash("prod")["locked"] is True
    assert summarize_stash("dev")["locked"] is False


def test_summarize_stash_pinned():
    assert summarize_stash("prod")["pinned"] is False


def test_summarize_stash_empty_values():
    result = summarize_stash("prod")
    assert result["empty_values"] == ["DEBUG"]


def test_summarize_stash_no_empty_values():
    result = summarize_stash("dev")
    assert result["empty_values"] == []


def test_summarize_stash_not_found():
    with pytest.raises(StashNotFoundError):
        summarize_stash("nonexistent")


def test_summarize_stash_longest_key():
    result = summarize_stash("prod")
    assert result["longest_key"] == "DB_HOST"


def test_summarize_all_returns_all():
    results = summarize_all()
    assert len(results) == 2


def test_summarize_all_sorted_by_name():
    results = summarize_all()
    names = [r["name"] for r in results]
    assert names == sorted(names)


def test_format_summary_contains_name():
    summary = summarize_stash("prod")
    output = format_summary(summary)
    assert "prod" in output


def test_format_summary_shows_locked():
    summary = summarize_stash("prod")
    output = format_summary(summary)
    assert "yes" in output


def test_format_summary_shows_tags():
    summary = summarize_stash("prod")
    output = format_summary(summary)
    assert "infra" in output
    assert "web" in output


def test_format_summary_no_tags_shows_none():
    summary = summarize_stash("dev")
    output = format_summary(summary)
    assert "(none)" in output


def test_format_summary_shows_empty_vars():
    summary = summarize_stash("prod")
    output = format_summary(summary)
    assert "DEBUG" in output
