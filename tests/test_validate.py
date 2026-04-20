"""Tests for stashpoint.validate module."""

import pytest
from stashpoint.validate import (
    validate_stash_name,
    validate_var_name,
    validate_var_value,
    validate_stash,
    MAX_STASH_NAME_LENGTH,
    MAX_VAR_NAME_LENGTH,
    MAX_VAR_VALUE_LENGTH,
    MAX_VARS_PER_STASH,
)


# --- validate_stash_name ---

def test_valid_stash_names():
    for name in ["myproject", "my-project", "my_project", "v1.0", "ABC123", "a"]:
        ok, msg = validate_stash_name(name)
        assert ok, f"Expected '{name}' to be valid, got: {msg}"


def test_stash_name_empty():
    ok, msg = validate_stash_name("")
    assert not ok
    assert "empty" in msg.lower()


def test_stash_name_too_long():
    ok, msg = validate_stash_name("a" * (MAX_STASH_NAME_LENGTH + 1))
    assert not ok
    assert "exceeds" in msg.lower()


def test_stash_name_invalid_chars():
    for name in ["my project", "my/project", "my@project", "name!"]:
        ok, msg = validate_stash_name(name)
        assert not ok, f"Expected '{name}' to be invalid"


# --- validate_var_name ---

def test_valid_var_names():
    for name in ["HOME", "_PRIVATE", "MY_VAR_1", "a"]:
        ok, msg = validate_var_name(name)
        assert ok, f"Expected '{name}' to be valid, got: {msg}"


def test_var_name_empty():
    ok, msg = validate_var_name("")
    assert not ok
    assert "empty" in msg.lower()


def test_var_name_starts_with_digit():
    ok, msg = validate_var_name("1VAR")
    assert not ok


def test_var_name_too_long():
    ok, msg = validate_var_name("A" * (MAX_VAR_NAME_LENGTH + 1))
    assert not ok
    assert "exceeds" in msg.lower()


def test_var_name_with_dash_invalid():
    ok, msg = validate_var_name("MY-VAR")
    assert not ok


# --- validate_var_value ---

def test_valid_var_value():
    ok, msg = validate_var_value("hello world")
    assert ok


def test_empty_var_value_is_valid():
    ok, msg = validate_var_value("")
    assert ok


def test_var_value_too_long():
    ok, msg = validate_var_value("x" * (MAX_VAR_VALUE_LENGTH + 1))
    assert not ok
    assert "exceeds" in msg.lower()


# --- validate_stash ---

def test_validate_stash_valid():
    errors = validate_stash("myproject", {"API_KEY": "abc123", "DEBUG": "true"})
    assert errors == []


def test_validate_stash_bad_name():
    errors = validate_stash("bad name!", {"KEY": "val"})
    assert any("stash name" in e.lower() for e in errors)


def test_validate_stash_bad_var_name():
    errors = validate_stash("good-name", {"1BADVAR": "value"})
    assert any("1BADVAR" in e for e in errors)


def test_validate_stash_too_many_vars():
    variables = {f"VAR_{i}": str(i) for i in range(MAX_VARS_PER_STASH + 1)}
    errors = validate_stash("myproject", variables)
    assert any("exceeding the maximum" in e for e in errors)


def test_validate_stash_multiple_errors():
    errors = validate_stash("bad name", {"1BAD": "x", "GOOD": "y"})
    assert len(errors) >= 2
