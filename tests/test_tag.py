import pytest
from unittest.mock import patch

from stashpoint.tag import add_tag, remove_tag, get_tags, find_by_tag, load_tags


@pytest.fixture
def mock_tags(tmp_path):
    with patch("stashpoint.tag.get_tag_path", return_value=tmp_path / "tags.json"):
        yield


def test_get_tags_empty(mock_tags):
    assert get_tags("myproject") == []


def test_add_tag(mock_tags):
    add_tag("myproject", "production")
    assert "production" in get_tags("myproject")


def test_add_tag_idempotent(mock_tags):
    add_tag("myproject", "production")
    add_tag("myproject", "production")
    assert get_tags("myproject").count("production") == 1


def test_add_multiple_tags(mock_tags):
    add_tag("myproject", "production")
    add_tag("myproject", "aws")
    tags = get_tags("myproject")
    assert "production" in tags
    assert "aws" in tags


def test_remove_tag(mock_tags):
    add_tag("myproject", "production")
    remove_tag("myproject", "production")
    assert "production" not in get_tags("myproject")


def test_remove_nonexistent_tag(mock_tags):
    remove_tag("myproject", "ghost")
    assert get_tags("myproject") == []


def test_find_by_tag(mock_tags):
    add_tag("proj-a", "aws")
    add_tag("proj-b", "aws")
    add_tag("proj-c", "gcp")
    result = find_by_tag("aws")
    assert result == ["proj-a", "proj-b"]


def test_find_by_tag_no_matches(mock_tags):
    assert find_by_tag("nonexistent") == []
