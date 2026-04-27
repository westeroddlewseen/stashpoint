"""Tests for stashpoint.dependency."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from stashpoint.dependency import (
    CircularDependencyError,
    DependencyAlreadyExistsError,
    StashNotFoundError,
    _would_create_cycle,
    add_dependency,
    get_dependencies,
    get_dependents,
    remove_dependency,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_env(stashes=None, existing_deps=None):
    """Return a context manager that patches storage and dependency I/O."""
    stashes = stashes or {}
    existing_deps = existing_deps or {}
    saved: dict = {}

    def _save(data):
        saved.clear()
        saved.update(data)

    ctx = patch.multiple(
        "stashpoint.dependency",
        load_stashes=MagicMock(return_value=stashes),
        load_dependencies=MagicMock(return_value=dict(existing_deps)),
        save_dependencies=MagicMock(side_effect=_save),
    )
    return ctx, saved


# ---------------------------------------------------------------------------
# _would_create_cycle
# ---------------------------------------------------------------------------

def test_no_cycle_empty_graph():
    assert not _would_create_cycle({}, "a", "b")


def test_direct_cycle_detected():
    # b -> a already; adding a -> b would cycle
    deps = {"b": ["a"]}
    assert _would_create_cycle(deps, "a", "b")


def test_transitive_cycle_detected():
    deps = {"b": ["c"], "c": ["a"]}
    assert _would_create_cycle(deps, "a", "b")


def test_no_cycle_unrelated_edges():
    deps = {"b": ["c"], "c": ["d"]}
    assert not _would_create_cycle(deps, "a", "b")


# ---------------------------------------------------------------------------
# add_dependency
# ---------------------------------------------------------------------------

def test_add_dependency_success():
    stashes = {"app": {}, "base": {}}
    ctx, saved = _mock_env(stashes=stashes)
    with ctx:
        add_dependency("app", "base")
    assert saved == {"app": ["base"]}


def test_add_dependency_stash_not_found():
    ctx, _ = _mock_env(stashes={"app": {}})
    with ctx:
        with pytest.raises(StashNotFoundError):
            add_dependency("app", "missing")


def test_add_dependency_already_exists():
    stashes = {"app": {}, "base": {}}
    existing = {"app": ["base"]}
    ctx, _ = _mock_env(stashes=stashes, existing_deps=existing)
    with ctx:
        with pytest.raises(DependencyAlreadyExistsError):
            add_dependency("app", "base")


def test_add_dependency_circular_raises():
    stashes = {"a": {}, "b": {}}
    existing = {"b": ["a"]}
    ctx, _ = _mock_env(stashes=stashes, existing_deps=existing)
    with ctx:
        with pytest.raises(CircularDependencyError):
            add_dependency("a", "b")


# ---------------------------------------------------------------------------
# remove_dependency
# ---------------------------------------------------------------------------

def test_remove_dependency_returns_true():
    existing = {"app": ["base"]}
    ctx, _ = _mock_env(existing_deps=existing)
    with ctx:
        result = remove_dependency("app", "base")
    assert result is True


def test_remove_dependency_not_found_returns_false():
    ctx, _ = _mock_env()
    with ctx:
        result = remove_dependency("app", "base")
    assert result is False


# ---------------------------------------------------------------------------
# get_dependencies / get_dependents
# ---------------------------------------------------------------------------

def test_get_dependencies_empty():
    ctx, _ = _mock_env()
    with ctx:
        assert get_dependencies("app") == []


def test_get_dependencies_returns_list():
    ctx, _ = _mock_env(existing_deps={"app": ["base", "shared"]})
    with ctx:
        assert get_dependencies("app") == ["base", "shared"]


def test_get_dependents_finds_reverse_edges():
    existing = {"app": ["base"], "other": ["base"]}
    ctx, _ = _mock_env(existing_deps=existing)
    with ctx:
        result = get_dependents("base")
    assert sorted(result) == ["app", "other"]


def test_get_dependents_empty_when_none():
    ctx, _ = _mock_env()
    with ctx:
        assert get_dependents("orphan") == []
