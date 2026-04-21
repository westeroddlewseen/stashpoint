"""Tests for stashpoint.annotate and stashpoint.cli_annotate."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from stashpoint.annotate import (
    set_annotation,
    get_annotation,
    remove_annotation,
    list_annotations,
    StashNotFoundError,
)
from stashpoint.cli_annotate import annotate_cmd


@pytest.fixture
def mock_annotations(tmp_path, monkeypatch):
    ann_file = tmp_path / "annotations.json"
    monkeypatch.setattr("stashpoint.annotate.get_annotation_path", lambda: ann_file)
    return ann_file


def test_get_annotation_missing_returns_none(mock_annotations):
    assert get_annotation("myproject") is None


def test_set_and_get_annotation(mock_annotations):
    set_annotation("myproject", "Production DB creds", stashes={"myproject": {}})
    assert get_annotation("myproject") == "Production DB creds"


def test_set_annotation_stash_not_found(mock_annotations):
    with pytest.raises(StashNotFoundError):
        set_annotation("ghost", "some note", stashes={"other": {}})


def test_set_annotation_no_stash_check(mock_annotations):
    set_annotation("anything", "note", stashes=None)
    assert get_annotation("anything") == "note"


def test_set_annotation_overwrites(mock_annotations):
    set_annotation("s", "old", stashes=None)
    set_annotation("s", "new", stashes=None)
    assert get_annotation("s") == "new"


def test_remove_annotation_existing(mock_annotations):
    set_annotation("s", "note", stashes=None)
    result = remove_annotation("s")
    assert result is True
    assert get_annotation("s") is None


def test_remove_annotation_nonexistent(mock_annotations):
    result = remove_annotation("ghost")
    assert result is False


def test_list_annotations_empty(mock_annotations):
    assert list_annotations() == {}


def test_list_annotations_multiple(mock_annotations):
    set_annotation("a", "note a", stashes=None)
    set_annotation("b", "note b", stashes=None)
    result = list_annotations()
    assert result == {"a": "note a", "b": "note b"}


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_set_annotation(runner, mock_annotations):
    with patch("stashpoint.cli_annotate.load_stashes", return_value={"proj": {}}):
        result = runner.invoke(annotate_cmd, ["set", "proj", "My project stash"])
    assert result.exit_code == 0
    assert "Annotation set" in result.output


def test_cli_set_annotation_not_found(runner, mock_annotations):
    with patch("stashpoint.cli_annotate.load_stashes", return_value={}):
        result = runner.invoke(annotate_cmd, ["set", "ghost", "note"])
    assert result.exit_code == 1


def test_cli_get_annotation(runner, mock_annotations):
    set_annotation("proj", "hello world", stashes=None)
    result = runner.invoke(annotate_cmd, ["get", "proj"])
    assert "hello world" in result.output


def test_cli_get_annotation_missing(runner, mock_annotations):
    result = runner.invoke(annotate_cmd, ["get", "missing"])
    assert "No annotation" in result.output


def test_cli_list_empty(runner, mock_annotations):
    result = runner.invoke(annotate_cmd, ["list"])
    assert "No annotations" in result.output


def test_cli_list_with_entries(runner, mock_annotations):
    set_annotation("a", "alpha", stashes=None)
    result = runner.invoke(annotate_cmd, ["list"])
    assert "a: alpha" in result.output
