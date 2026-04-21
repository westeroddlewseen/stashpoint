"""Tests for stashpoint.watch."""

import pytest
from unittest.mock import patch, call

from stashpoint.watch import (
    _stash_fingerprint,
    get_changes,
    poll_stash,
    StashNotFoundError,
)


def test_fingerprint_is_stable():
    vars1 = {"A": "1", "B": "2"}
    assert _stash_fingerprint(vars1) == _stash_fingerprint(vars1)


def test_fingerprint_differs_on_change():
    assert _stash_fingerprint({"A": "1"}) != _stash_fingerprint({"A": "2"})


def test_fingerprint_order_independent():
    a = {"X": "1", "Y": "2"}
    b = {"Y": "2", "X": "1"}
    assert _stash_fingerprint(a) == _stash_fingerprint(b)


def test_get_changes_added():
    result = get_changes({}, {"NEW": "val"})
    assert result["added"] == {"NEW": "val"}
    assert result["removed"] == {}
    assert result["changed"] == {}


def test_get_changes_removed():
    result = get_changes({"OLD": "val"}, {})
    assert result["removed"] == {"OLD": "val"}
    assert result["added"] == {}


def test_get_changes_changed():
    result = get_changes({"K": "before"}, {"K": "after"})
    assert result["changed"] == {"K": ("before", "after")}


def test_get_changes_no_diff():
    result = get_changes({"K": "v"}, {"K": "v"})
    assert result == {"added": {}, "removed": {}, "changed": {}}


def test_poll_stash_raises_if_not_found():
    with patch("stashpoint.watch.load_stash", return_value=None):
        with pytest.raises(StashNotFoundError):
            poll_stash("missing", max_polls=0)


def test_poll_stash_calls_on_change():
    initial = {"A": "1"}
    updated = {"A": "2"}
    side_effects = [initial, updated]

    changes = []

    with patch("stashpoint.watch.load_stash", side_effect=side_effects), \
         patch("stashpoint.watch.time.sleep"):
        poll_stash(
            "myenv",
            interval=0,
            max_polls=1,
            on_change=lambda n, o, nw: changes.append((n, o, nw)),
        )

    assert len(changes) == 1
    assert changes[0] == ("myenv", {"A": "1"}, {"A": "2"})


def test_poll_stash_no_change_no_callback():
    stash = {"A": "1"}
    calls = []

    with patch("stashpoint.watch.load_stash", return_value=stash), \
         patch("stashpoint.watch.time.sleep"):
        poll_stash(
            "env",
            interval=0,
            max_polls=3,
            on_change=lambda *a: calls.append(a),
        )

    assert calls == []


def test_poll_stash_raises_if_deleted_mid_watch():
    with patch("stashpoint.watch.load_stash", side_effect=[{"A": "1"}, None]), \
         patch("stashpoint.watch.time.sleep"):
        with pytest.raises(StashNotFoundError, match="deleted"):
            poll_stash("env", interval=0, max_polls=1)
