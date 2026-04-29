"""Tests for stashpoint.weight."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from stashpoint.weight import (
    set_weight,
    get_weight,
    remove_weight,
    ranked_stashes,
    StashNotFoundError,
    InvalidWeightError,
    WEIGHT_MIN,
    WEIGHT_MAX,
)


@pytest.fixture()
def mock_weights(tmp_path, monkeypatch):
    weight_file = tmp_path / "weights.json"
    monkeypatch.setattr("stashpoint.weight.get_weight_path", lambda: weight_file)
    return weight_file


@pytest.fixture()
def mock_stashes():
    with patch("stashpoint.weight.load_stashes", return_value={"alpha": {}, "beta": {}}) as m:
        yield m


def test_set_weight_stores_value(mock_weights, mock_stashes):
    result = set_weight("alpha", 200)
    assert result == 200
    assert get_weight("alpha") == 200


def test_set_weight_stash_not_found(mock_weights, mock_stashes):
    with pytest.raises(StashNotFoundError):
        set_weight("missing", 100)


def test_set_weight_invalid_low(mock_weights, mock_stashes):
    with pytest.raises(InvalidWeightError):
        set_weight("alpha", WEIGHT_MIN - 1)


def test_set_weight_invalid_high(mock_weights, mock_stashes):
    with pytest.raises(InvalidWeightError):
        set_weight("alpha", WEIGHT_MAX + 1)


def test_set_weight_invalid_type(mock_weights, mock_stashes):
    with pytest.raises(InvalidWeightError):
        set_weight("alpha", "heavy")  # type: ignore[arg-type]


def test_set_weight_boundary_values(mock_weights, mock_stashes):
    assert set_weight("alpha", WEIGHT_MIN) == WEIGHT_MIN
    assert set_weight("beta", WEIGHT_MAX) == WEIGHT_MAX


def test_get_weight_default(mock_weights):
    assert get_weight("nonexistent") == 500
    assert get_weight("nonexistent", default=0) == 0


def test_remove_weight_existing(mock_weights, mock_stashes):
    set_weight("alpha", 300)
    removed = remove_weight("alpha")
    assert removed is True
    assert get_weight("alpha") == 500  # back to default


def test_remove_weight_nonexistent(mock_weights):
    removed = remove_weight("ghost")
    assert removed is False


def test_ranked_stashes_order(mock_weights, mock_stashes):
    set_weight("alpha", 100)
    set_weight("beta", 800)
    ranked = ranked_stashes()
    names = [n for n, _ in ranked]
    assert names.index("beta") < names.index("alpha")


def test_ranked_stashes_uses_default_for_unset(mock_weights, mock_stashes):
    # only alpha has an explicit weight below default
    set_weight("alpha", 10)
    ranked = ranked_stashes(default=500)
    weights_map = dict(ranked)
    assert weights_map["beta"] == 500
    assert weights_map["alpha"] == 10
