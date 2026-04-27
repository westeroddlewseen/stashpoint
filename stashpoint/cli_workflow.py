"""CLI commands for managing and running stashpoint workflows."""
from __future__ import annotations

import json

import click

from stashpoint.workflow import (
    InvalidWorkflowStepError,
    WorkflowAlreadyExistsError,
    WorkflowNotFoundError,
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
    run_workflow,
)


@click.group("workflow")
def workflow_cmd():
    """Manage and run named workflows."""


@workflow_cmd.command("create")
@click.argument("name")
@click.argument("steps_json")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing workflow.")
def create_cmd(name: str, steps_json: str, overwrite: bool):
    """Create a workflow from a JSON steps definition."""
    try:
        steps = json.loads(steps_json)
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid JSON: {exc}") from exc
    try:
        create_workflow(name, steps, overwrite=overwrite)
        click.echo(f"Workflow '{name}' created with {len(steps)} step(s).")
    except WorkflowAlreadyExistsError as exc:
        raise click.ClickException(str(exc)) from exc
    except InvalidWorkflowStepError as exc:
        raise click.ClickException(str(exc)) from exc


@workflow_cmd.command("delete")
@click.argument("name")
def delete_cmd(name: str):
    """Delete a workflow by name."""
    try:
        delete_workflow(name)
        click.echo(f"Workflow '{name}' deleted.")
    except WorkflowNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc


@workflow_cmd.command("show")
@click.argument("name")
def show_cmd(name: str):
    """Show the steps of a workflow."""
    try:
        wf = get_workflow(name)
    except WorkflowNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Workflow: {name}")
    for i, step in enumerate(wf["steps"], 1):
        click.echo(f"  {i}. {json.dumps(step)}")


@workflow_cmd.command("list")
def list_cmd():
    """List all saved workflows."""
    names = list_workflows()
    if not names:
        click.echo("No workflows saved.")
        return
    for name in names:
        click.echo(name)


@workflow_cmd.command("run")
@click.argument("name")
@click.option("--quiet", is_flag=True, default=False, help="Suppress step-by-step output.")
def run_cmd(name: str, quiet: bool):
    """Execute all steps in a workflow."""
    try:
        log = run_workflow(name)
    except WorkflowNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Workflow failed: {exc}") from exc
    if not quiet:
        for entry in log:
            click.echo(entry)
    click.echo(f"Workflow '{name}' completed ({len(log)} step(s)).")
