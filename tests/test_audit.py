"""Tests for stashpoint.audit."""

import pytest
from pathlib import Path
from stashpoint.audit import (
    load_audit,
    save_audit,
    record_audit,
    get_stash_audit,
    clear_audit,
)


@pytest.fixture
def audit_file(tmp_path):
    return tmp_path / "audit.json"


def test_load_audit_empty(audit_file):
    result = load_audit(audit_file)
    assert result == []


def test_record_audit_saves_entry(audit_file):
    entry = record_audit("save", "myproject", path=audit_file)
    assert entry["action"] == "save"
    assert entry["stash"] == "myproject"
    assert entry["detail"] is None
    assert "timestamp" in entry


def test_record_audit_with_detail(audit_file):
    entry = record_audit("load", "myproject", detail="bash", path=audit_file)
    assert entry["detail"] == "bash"


def test_record_multiple_entries(audit_file):
    record_audit("save", "proj1", path=audit_file)
    record_audit("load", "proj1", path=audit_file)
    record_audit("delete", "proj2", path=audit_file)
    entries = load_audit(audit_file)
    assert len(entries) == 3


def test_get_stash_audit_filters_by_name(audit_file):
    record_audit("save", "alpha", path=audit_file)
    record_audit("save", "beta", path=audit_file)
    record_audit("load", "alpha", path=audit_file)
    result = get_stash_audit("alpha", path=audit_file)
    assert len(result) == 2
    assert all(e["stash"] == "alpha" for e in result)


def test_get_stash_audit_no_match(audit_file):
    record_audit("save", "alpha", path=audit_file)
    result = get_stash_audit("nonexistent", path=audit_file)
    assert result == []


def test_clear_audit(audit_file):
    record_audit("save", "proj", path=audit_file)
    record_audit("load", "proj", path=audit_file)
    clear_audit(audit_file)
    assert load_audit(audit_file) == []


def test_audit_entry_timestamp_is_utc(audit_file):
    entry = record_audit("save", "proj", path=audit_file)
    assert entry["timestamp"].endswith("+00:00")


def test_audit_persists_across_loads(audit_file):
    record_audit("save", "proj", path=audit_file)
    loaded = load_audit(audit_file)
    assert len(loaded) == 1
    assert loaded[0]["action"] == "save"
