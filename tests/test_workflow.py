"""Tests for stashpoint.workflow."""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from stashpoint.workflow import (
    InvalidWorkflowStepError,
    WorkflowAlreadyExistsError,
    WorkflowNotFoundError,
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
    load_workflows,
    save_workflows,
)


@pytest.fixture()
def mock_workflows(tmp_path, monkeypatch):
    wf_file = tmp_path / "workflows.json"
    monkeypatch.setattr("stashpoint.workflow.get_workflow_path", lambda: wf_file)
    return wf_file


def test_list_workflows_empty(mock_workflows):
    assert list_workflows() == []


def test_create_and_list_workflow(mock_workflows):
    create_workflow("deploy", [{"action": "load", "stash": "prod"}])
    assert list_workflows() == ["deploy"]


def test_create_workflow_invalid_action(mock_workflows):
    with pytest.raises(InvalidWorkflowStepError):
        create_workflow("bad", [{"action": "explode", "stash": "x"}])


def test_create_workflow_already_exists_raises(mock_workflows):
    create_workflow("ci", [{"action": "load", "stash": "test"}])
    with pytest.raises(WorkflowAlreadyExistsError):
        create_workflow("ci", [{"action": "load", "stash": "test"}])


def test_create_workflow_overwrite(mock_workflows):
    create_workflow("ci", [{"action": "load", "stash": "test"}])
    create_workflow("ci", [{"action": "save", "stash": "test", "vars": {}}], overwrite=True)
    wf = get_workflow("ci")
    assert wf["steps"][0]["action"] == "save"


def test_get_workflow_not_found(mock_workflows):
    with pytest.raises(WorkflowNotFoundError):
        get_workflow("ghost")


def test_delete_workflow(mock_workflows):
    create_workflow("tmp", [{"action": "load", "stash": "x"}])
    delete_workflow("tmp")
    assert "tmp" not in list_workflows()


def test_delete_workflow_not_found(mock_workflows):
    with pytest.raises(WorkflowNotFoundError):
        delete_workflow("nope")


def test_list_workflows_sorted(mock_workflows):
    create_workflow("zebra", [{"action": "load", "stash": "z"}])
    create_workflow("alpha", [{"action": "load", "stash": "a"}])
    assert list_workflows() == ["alpha", "zebra"]


def test_get_workflow_returns_copy(mock_workflows):
    create_workflow("w", [{"action": "load", "stash": "s"}])
    wf = get_workflow("w")
    wf["steps"].append({"action": "delete", "stash": "s"})
    assert len(get_workflow("w")["steps"]) == 1
