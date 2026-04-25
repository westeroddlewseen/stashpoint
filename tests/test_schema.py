"""Tests for stashpoint.schema versioning and migration."""

import pytest
from stashpoint.schema import (
    CURRENT_SCHEMA_VERSION,
    SchemaMigrationError,
    detect_version,
    migrate,
    unwrap,
    wrap,
)


# ---------------------------------------------------------------------------
# detect_version
# ---------------------------------------------------------------------------

def test_detect_version_v1_plain_dict():
    data = {"my_stash": {"FOO": "bar"}}
    assert detect_version(data) == 1


def test_detect_version_explicit():
    data = {"schema_version": 2, "stashes": {}}
    assert detect_version(data) == 2


def test_detect_version_string_coerced_to_int():
    data = {"schema_version": "2", "stashes": {}}
    assert detect_version(data) == 2


# ---------------------------------------------------------------------------
# migrate
# ---------------------------------------------------------------------------

def test_migrate_v1_adds_schema_version():
    data = {"prod": {"DB_HOST": "localhost"}}
    result = migrate(data)
    assert result["schema_version"] == 2


def test_migrate_v1_preserves_stashes():
    data = {"prod": {"DB_HOST": "localhost"}}
    result = migrate(data)
    assert result["stashes"] == {"prod": {"DB_HOST": "localhost"}}


def test_migrate_already_current_is_noop():
    data = {"schema_version": 2, "stashes": {"a": {"X": "1"}}}
    result = migrate(data)
    assert result == data


def test_migrate_unknown_version_raises():
    data = {"schema_version": 99, "stashes": {}}
    with pytest.raises(SchemaMigrationError):
        migrate(data)


# ---------------------------------------------------------------------------
# wrap / unwrap
# ---------------------------------------------------------------------------

def test_wrap_adds_version_and_stashes_key():
    stashes = {"dev": {"ENV": "development"}}
    result = wrap(stashes)
    assert result["schema_version"] == CURRENT_SCHEMA_VERSION
    assert result["stashes"] is stashes


def test_unwrap_versioned_structure():
    stashes = {"dev": {"ENV": "development"}}
    data = {"schema_version": 2, "stashes": stashes}
    assert unwrap(data) is stashes


def test_unwrap_plain_dict_returns_self():
    data = {"dev": {"ENV": "development"}}
    assert unwrap(data) is data


def test_wrap_then_unwrap_roundtrip():
    stashes = {"ci": {"CI": "true"}}
    assert unwrap(wrap(stashes)) == stashes
