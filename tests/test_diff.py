"""Tests for stashpoint.diff module."""
import pytest
from stashpoint.diff import diff_stashes, format_diff


def test_diff_identical_stashes():
    a = {"FOO": "bar", "BAZ": "qux"}
    result = diff_stashes(a, a.copy())
    assert result == {}


def test_diff_added_key():
    a = {"FOO": "bar"}
    b = {"FOO": "bar", "NEW": "val"}
    result = diff_stashes(a, b)
    assert result == {"NEW": (None, "val")}


def test_diff_removed_key():
    a = {"FOO": "bar", "OLD": "val"}
    b = {"FOO": "bar"}
    result = diff_stashes(a, b)
    assert result == {"OLD": ("val", None)}


def test_diff_changed_value():
    a = {"FOO": "old"}
    b = {"FOO": "new"}
    result = diff_stashes(a, b)
    assert result == {"FOO": ("old", "new")}


def test_diff_multiple_changes():
    a = {"A": "1", "B": "2", "C": "3"}
    b = {"A": "1", "B": "changed", "D": "4"}
    result = diff_stashes(a, b)
    assert "B" in result
    assert "C" in result
    assert "D" in result
    assert "A" not in result


def test_format_diff_no_differences():
    lines = format_diff({}, "alpha", "beta")
    assert len(lines) == 1
    assert "No differences" in lines[0]


def test_format_diff_added():
    diffs = {"NEW": (None, "val")}
    lines = format_diff(diffs, "a", "b")
    assert any(line.startswith("  +") and "NEW=val" in line for line in lines)


def test_format_diff_removed():
    diffs = {"OLD": ("val", None)}
    lines = format_diff(diffs, "a", "b")
    assert any(line.startswith("  -") and "OLD=val" in line for line in lines)


def test_format_diff_changed():
    diffs = {"FOO": ("old", "new")}
    lines = format_diff(diffs, "a", "b")
    assert any(line.startswith("  ~") and "FOO" in line for line in lines)
