"""Tests for stashpoint.archive module."""

import json
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from stashpoint.archive import (
    ArchiveError,
    StashNotFoundError,
    create_archive,
    restore_archive,
    ARCHIVE_MANIFEST,
    STASHES_FILE,
)

SAMPLE_STASHES = {
    "prod": {"DB_HOST": "prod.db", "DEBUG": "false"},
    "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
}


def _make_archive(tmp_path, stashes, names):
    """Helper: write a valid archive ZIP to tmp_path/archive.zip."""
    dest = tmp_path / "archive.zip"
    selected = {n: stashes[n] for n in names}
    manifest = {"version": 1, "stashes": names}
    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr(ARCHIVE_MANIFEST, json.dumps(manifest))
        zf.writestr(STASHES_FILE, json.dumps(selected))
    return str(dest)


@patch("stashpoint.archive.load_stashes", return_value=SAMPLE_STASHES)
@patch("stashpoint.archive.save_stashes")
def test_create_archive_produces_zip(mock_save, mock_load, tmp_path):
    dest = str(tmp_path / "out.zip")
    result = create_archive(["prod"], dest)
    assert Path(dest).exists()
    assert result["archived"] == ["prod"]
    assert result["path"] == dest


@patch("stashpoint.archive.load_stashes", return_value=SAMPLE_STASHES)
@patch("stashpoint.archive.save_stashes")
def test_create_archive_zip_contains_stash_data(mock_save, mock_load, tmp_path):
    dest = str(tmp_path / "out.zip")
    create_archive(["dev"], dest)
    with zipfile.ZipFile(dest, "r") as zf:
        data = json.loads(zf.read(STASHES_FILE))
    assert "dev" in data
    assert data["dev"]["DEBUG"] == "true"


@patch("stashpoint.archive.load_stashes", return_value=SAMPLE_STASHES)
def test_create_archive_missing_stash_raises(mock_load, tmp_path):
    dest = str(tmp_path / "out.zip")
    with pytest.raises(StashNotFoundError, match="staging"):
        create_archive(["prod", "staging"], dest)


@patch("stashpoint.archive.load_stashes", return_value={})
@patch("stashpoint.archive.save_stashes")
def test_restore_archive_imports_stashes(mock_save, mock_load, tmp_path):
    archive_path = _make_archive(tmp_path, SAMPLE_STASHES, ["prod"])
    result = restore_archive(archive_path)
    assert "prod" in result["restored"]
    assert result["skipped"] == []
    saved = mock_save.call_args[0][0]
    assert saved["prod"] == SAMPLE_STASHES["prod"]


@patch("stashpoint.archive.load_stashes", return_value={"prod": {"DB_HOST": "old"}})
@patch("stashpoint.archive.save_stashes")
def test_restore_archive_skips_existing_without_overwrite(mock_save, mock_load, tmp_path):
    archive_path = _make_archive(tmp_path, SAMPLE_STASHES, ["prod"])
    result = restore_archive(archive_path, overwrite=False)
    assert "prod" in result["skipped"]
    assert result["restored"] == []


@patch("stashpoint.archive.load_stashes", return_value={"prod": {"DB_HOST": "old"}})
@patch("stashpoint.archive.save_stashes")
def test_restore_archive_overwrites_when_flag_set(mock_save, mock_load, tmp_path):
    archive_path = _make_archive(tmp_path, SAMPLE_STASHES, ["prod"])
    result = restore_archive(archive_path, overwrite=True)
    assert "prod" in result["restored"]
    saved = mock_save.call_args[0][0]
    assert saved["prod"]["DB_HOST"] == "prod.db"


def test_restore_archive_file_not_found(tmp_path):
    with pytest.raises(ArchiveError, match="not found"):
        restore_archive(str(tmp_path / "missing.zip"))


def test_restore_archive_invalid_zip(tmp_path):
    bad = tmp_path / "bad.zip"
    bad.write_text("not a zip")
    with pytest.raises(ArchiveError):
        restore_archive(str(bad))
