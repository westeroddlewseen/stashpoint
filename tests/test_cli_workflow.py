"""Tests for stashpoint.cli_workflow."""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from stashpoint.cli_workflow import workflow_cmd
from stashpoint.workflow import WorkflowNotFoundError, WorkflowAlreadyExistsError


@pytest.fixture()
def runner():
    return CliRunner()


def test_create_workflow_success(runner):
    steps = json.dumps([{"action": "load", "stash": "prod"}])
    with patch("stashpoint.cli_workflow.create_workflow") as mock_create:
        result = runner.invoke(workflow_cmd, ["create", "deploy", steps])
    assert result.exit_code == 0
    assert "created" in result.output
    mock_create.assert_called_once()


def test_create_workflow_already_exists(runner):
    steps = json.dumps([{"action": "load", "stash": "prod"}])
    with patch("stashpoint.cli_workflow.create_workflow", side_effect=WorkflowAlreadyExistsError("exists")):
        result = runner.invoke(workflow_cmd, ["create", "deploy", steps])
    assert result.exit_code != 0
    assert "exists" in result.output


def test_create_workflow_invalid_json(runner):
    result = runner.invoke(workflow_cmd, ["create", "deploy", "not-json"])
    assert result.exit_code != 0
    assert "Invalid JSON" in result.output


def test_delete_workflow_success(runner):
    with patch("stashpoint.cli_workflow.delete_workflow") as mock_del:
        result = runner.invoke(workflow_cmd, ["delete", "deploy"])
    assert result.exit_code == 0
    assert "deleted" in result.output
    mock_del.assert_called_once_with("deploy")


def test_delete_workflow_not_found(runner):
    with patch("stashpoint.cli_workflow.delete_workflow", side_effect=WorkflowNotFoundError("missing")):
        result = runner.invoke(workflow_cmd, ["delete", "ghost"])
    assert result.exit_code != 0


def test_list_workflows_empty(runner):
    with patch("stashpoint.cli_workflow.list_workflows", return_value=[]):
        result = runner.invoke(workflow_cmd, ["list"])
    assert "No workflows" in result.output


def test_list_workflows_shows_names(runner):
    with patch("stashpoint.cli_workflow.list_workflows", return_value=["ci", "deploy"]):
        result = runner.invoke(workflow_cmd, ["list"])
    assert "ci" in result.output
    assert "deploy" in result.output


def test_show_workflow(runner):
    wf = {"steps": [{"action": "load", "stash": "prod"}]}
    with patch("stashpoint.cli_workflow.get_workflow", return_value=wf):
        result = runner.invoke(workflow_cmd, ["show", "deploy"])
    assert "load" in result.output


def test_run_workflow_success(runner):
    with patch("stashpoint.cli_workflow.run_workflow", return_value=["Step 1: loaded 'prod'"]):
        result = runner.invoke(workflow_cmd, ["run", "deploy"])
    assert result.exit_code == 0
    assert "completed" in result.output


def test_run_workflow_quiet_suppresses_steps(runner):
    with patch("stashpoint.cli_workflow.run_workflow", return_value=["Step 1: loaded 'prod'"]):
        result = runner.invoke(workflow_cmd, ["run", "--quiet", "deploy"])
    assert "Step 1" not in result.output
    assert "completed" in result.output


def test_run_workflow_not_found(runner):
    with patch("stashpoint.cli_workflow.run_workflow", side_effect=WorkflowNotFoundError("nope")):
        result = runner.invoke(workflow_cmd, ["run", "ghost"])
    assert result.exit_code != 0
