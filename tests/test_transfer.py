"""Tests for stashpoint.transfer module."""

import json
import pytest
from pathlib import Path

from stashpoint.transfer import (
    transfer_stash,
    list_transfer_targets,
    StashNotFoundError,
    StashAlreadyExistsError,
    InvalidDirectoryError,
)


@pytest.fixture
def source_dir(tmp_path):
    d = tmp_path / "source"
    d.mkdir()
    stashes = {"myapp": {"DB_HOST": "localhost", "PORT": "5432"}, "other": {"X": "1"}}
    (d / "stashes.json").write_text(json.dumps(stashes))
    return str(d)


@pytest.fixture
def dest_dir(tmp_path):
    d = tmp_path / "dest"
    d.mkdir()
    return str(d)


def test_transfer_copies_stash(source_dir, dest_dir):
    result = transfer_stash("myapp", source_dir, dest_dir)
    assert result["name"] == "myapp"
    assert result["moved"] is False
    stashes_file = Path(dest_dir) / "stashes.json"
    data = json.loads(stashes_file.read_text())
    assert "myapp" in data
    assert data["myapp"]["DB_HOST"] == "localhost"


def test_transfer_copy_leaves_source_intact(source_dir, dest_dir):
    transfer_stash("myapp", source_dir, dest_dir, move=False)
    src_data = json.loads((Path(source_dir) / "stashes.json").read_text())
    assert "myapp" in src_data


def test_transfer_move_removes_from_source(source_dir, dest_dir):
    transfer_stash("myapp", source_dir, dest_dir, move=True)
    src_data = json.loads((Path(source_dir) / "stashes.json").read_text())
    assert "myapp" not in src_data
    assert "other" in src_data  # other stashes untouched


def test_transfer_stash_not_found(source_dir, dest_dir):
    with pytest.raises(StashNotFoundError):
        transfer_stash("nonexistent", source_dir, dest_dir)


def test_transfer_invalid_source(tmp_path, dest_dir):
    with pytest.raises(InvalidDirectoryError):
        transfer_stash("myapp", str(tmp_path / "no_such_dir"), dest_dir)


def test_transfer_creates_dest_if_missing(source_dir, tmp_path):
    new_dest = str(tmp_path / "brand_new")
    transfer_stash("myapp", source_dir, new_dest)
    assert (Path(new_dest) / "stashes.json").exists()


def test_transfer_no_overwrite_raises(source_dir, dest_dir):
    transfer_stash("myapp", source_dir, dest_dir)
    with pytest.raises(StashAlreadyExistsError):
        transfer_stash("myapp", source_dir, dest_dir, overwrite=False)


def test_transfer_overwrite_replaces(source_dir, dest_dir):
    transfer_stash("myapp", source_dir, dest_dir)
    # Modify source stash
    src_data = json.loads((Path(source_dir) / "stashes.json").read_text())
    src_data["myapp"]["DB_HOST"] = "remotehost"
    (Path(source_dir) / "stashes.json").write_text(json.dumps(src_data))
    transfer_stash("myapp", source_dir, dest_dir, overwrite=True)
    dest_data = json.loads((Path(dest_dir) / "stashes.json").read_text())
    assert dest_data["myapp"]["DB_HOST"] == "remotehost"


def test_list_transfer_targets_empty(dest_dir):
    result = list_transfer_targets(dest_dir)
    assert result == []


def test_list_transfer_targets_returns_sorted(source_dir):
    result = list_transfer_targets(source_dir)
    assert result == ["myapp", "other"]
