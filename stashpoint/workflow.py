"""Workflow support: named sequences of stash operations to run in order."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from stashpoint.storage import load_stashes


class WorkflowNotFoundError(Exception):
    pass


class WorkflowAlreadyExistsError(Exception):
    pass


class InvalidWorkflowStepError(Exception):
    pass


VALID_ACTIONS = {"load", "save", "delete", "copy", "merge"}


def get_workflow_path() -> Path:
    base = Path.home() / ".stashpoint"
    base.mkdir(parents=True, exist_ok=True)
    return base / "workflows.json"


def load_workflows() -> dict[str, Any]:
    path = get_workflow_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_workflows(workflows: dict[str, Any]) -> None:
    get_workflow_path().write_text(json.dumps(workflows, indent=2))


def create_workflow(name: str, steps: list[dict], overwrite: bool = False) -> None:
    workflows = load_workflows()
    if name in workflows and not overwrite:
        raise WorkflowAlreadyExistsError(f"Workflow '{name}' already exists.")
    for step in steps:
        action = step.get("action")
        if action not in VALID_ACTIONS:
            raise InvalidWorkflowStepError(
                f"Invalid action '{action}'. Must be one of: {sorted(VALID_ACTIONS)}"
            )
    workflows[name] = {"steps": steps}
    save_workflows(workflows)


def get_workflow(name: str) -> dict[str, Any]:
    workflows = load_workflows()
    if name not in workflows:
        raise WorkflowNotFoundError(f"Workflow '{name}' not found.")
    return dict(workflows[name])


def delete_workflow(name: str) -> None:
    workflows = load_workflows()
    if name not in workflows:
        raise WorkflowNotFoundError(f"Workflow '{name}' not found.")
    del workflows[name]
    save_workflows(workflows)


def list_workflows() -> list[str]:
    return sorted(load_workflows().keys())


def run_workflow(name: str) -> list[str]:
    """Execute a workflow and return a log of completed step descriptions."""
    from stashpoint.copy import copy_stash
    from stashpoint.merge import merge_stashes
    from stashpoint.storage import delete_stash, load_stash

    workflow = get_workflow(name)
    log: list[str] = []
    for i, step in enumerate(workflow["steps"], 1):
        action = step["action"]
        if action == "load":
            load_stash(step["stash"])
            log.append(f"Step {i}: loaded '{step['stash']}'")  
        elif action == "save":
            from stashpoint.storage import save_stash
            save_stash(step["stash"], step.get("vars", {}))
            log.append(f"Step {i}: saved '{step['stash']}'")  
        elif action == "delete":
            delete_stash(step["stash"])
            log.append(f"Step {i}: deleted '{step['stash']}'")  
        elif action == "copy":
            copy_stash(step["source"], step["destination"], overwrite=step.get("overwrite", False))
            log.append(f"Step {i}: copied '{step['source']}' -> '{step['destination']}'")  
        elif action == "merge":
            merge_stashes(step["source"], step["target"], overwrite=step.get("overwrite", False))
            log.append(f"Step {i}: merged '{step['source']}' into '{step['target']}'")  
    return log
