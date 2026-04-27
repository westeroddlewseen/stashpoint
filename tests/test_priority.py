"""Tests for stashpoint.priority."""

import pytest
from unittest.mock import patch

from stashpoint.priority import (
    StashNotFoundError,
    InvalidPriorityError,
    set_priority,
    get_priority,
    remove_priority,
    rank_by_priority,
    DEFAULT_PRIORITY,
)

SAMPLE_STASHES = {"alpha": {"A": "1"}, "beta": {"B": "2"}, "gamma": {"C": "3"}}


@pytest.fixture()
def mock_priorities(tmp_path, monkeypatch):
    store = {}

    monkeypatch.setattr("stashpoint.priority.load_priorities", lambda: dict(store))
    monkeypatch.setattr(
        "stashpoint.priority.save_priorities",
        lambda d: store.update(d) or store.update({k: v for k, v in store.items() if k in d})
        or [store.pop(k) for k in list(store) if k not in d],
    )
    monkeypatch.setattr("stashpoint.priority.load_stashes", lambda: SAMPLE_STASHES)
    return store


def test_set_priority_stores_value(mock_priorities):
    set_priority("alpha", 8)
    assert mock_priorities["alpha"] == 8


def test_set_priority_stash_not_found():
    with patch("stashpoint.priority.load_stashes", return_value={}):
        with patch("stashpoint.priority.load_priorities", return_value={}):
            with patch("stashpoint.priority.save_priorities"):
                with pytest.raises(StashNotFoundError):
                    set_priority("missing", 5)


def test_set_priority_invalid_low():
    with patch("stashpoint.priority.load_stashes", return_value=SAMPLE_STASHES):
        with pytest.raises(InvalidPriorityError):
            set_priority("alpha", 0)


def test_set_priority_invalid_high():
    with patch("stashpoint.priority.load_stashes", return_value=SAMPLE_STASHES):
        with pytest.raises(InvalidPriorityError):
            set_priority("alpha", 11)


def test_get_priority_returns_default_when_unset():
    with patch("stashpoint.priority.load_priorities", return_value={}):
        assert get_priority("alpha") == DEFAULT_PRIORITY


def test_get_priority_returns_stored_value():
    with patch("stashpoint.priority.load_priorities", return_value={"alpha": 9}):
        assert get_priority("alpha") == 9


def test_remove_priority_returns_true_when_present(mock_priorities):
    mock_priorities["beta"] = 7
    result = remove_priority("beta")
    assert result is True
    assert "beta" not in mock_priorities


def test_remove_priority_returns_false_when_absent(mock_priorities):
    result = remove_priority("nonexistent")
    assert result is False


def test_rank_by_priority_highest_first():
    with patch(
        "stashpoint.priority.load_priorities",
        return_value={"alpha": 3, "beta": 9, "gamma": 6},
    ):
        ranked = rank_by_priority(["alpha", "beta", "gamma"])
    assert ranked == ["beta", "gamma", "alpha"]


def test_rank_by_priority_uses_default_for_unset():
    with patch("stashpoint.priority.load_priorities", return_value={"alpha": 8}):
        ranked = rank_by_priority(["alpha", "beta"])
    assert ranked[0] == "alpha"


def test_set_priority_no_stash_check():
    with patch("stashpoint.priority.load_priorities", return_value={}) as _lp:
        with patch("stashpoint.priority.save_priorities") as mock_save:
            set_priority("ghost", 7, check_exists=False)
            mock_save.assert_called_once_with({"ghost": 7})
