"""CLI commands for stash dependency management."""

from __future__ import annotations

import click

from stashpoint.dependency import (
    CircularDependencyError,
    DependencyAlreadyExistsError,
    StashNotFoundError,
    add_dependency,
    get_dependencies,
    get_dependents,
    remove_dependency,
)


@click.group("dependency")
def dependency_cmd():
    """Manage stash dependencies."""


@dependency_cmd.command("add")
@click.argument("stash")
@click.argument("depends_on")
def add_cmd(stash: str, depends_on: str) -> None:
    """Record that STASH depends on DEPENDS_ON."""
    try:
        add_dependency(stash, depends_on)
        click.echo(f"Added dependency: {stash} -> {depends_on}")
    except StashNotFoundError as exc:
        click.echo(f"Error: stash '{exc}' not found.", err=True)
        raise SystemExit(1)
    except DependencyAlreadyExistsError:
        click.echo(f"'{depends_on}' is already a dependency of '{stash}'.")
    except CircularDependencyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@dependency_cmd.command("remove")
@click.argument("stash")
@click.argument("depends_on")
def remove_cmd(stash: str, depends_on: str) -> None:
    """Remove a dependency edge from STASH to DEPENDS_ON."""
    removed = remove_dependency(stash, depends_on)
    if removed:
        click.echo(f"Removed dependency: {stash} -> {depends_on}")
    else:
        click.echo(f"No dependency from '{stash}' to '{depends_on}' found.")


@dependency_cmd.command("list")
@click.argument("stash")
@click.option("--reverse", is_flag=True, help="Show stashes that depend on STASH instead.")
def list_cmd(stash: str, reverse: bool) -> None:
    """List dependencies of STASH (or its dependents with --reverse)."""
    if reverse:
        items = get_dependents(stash)
        label = f"Stashes that depend on '{stash}'"
    else:
        items = get_dependencies(stash)
        label = f"Dependencies of '{stash}'"

    if not items:
        click.echo(f"{label}: (none)")
    else:
        click.echo(f"{label}:")
        for item in sorted(items):
            click.echo(f"  {item}")
