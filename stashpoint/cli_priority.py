"""CLI commands for stash priority management."""

import click

from stashpoint.priority import (
    StashNotFoundError,
    InvalidPriorityError,
    set_priority,
    get_priority,
    remove_priority,
    load_priorities,
    rank_by_priority,
    DEFAULT_PRIORITY,
)
from stashpoint.storage import load_stashes


@click.group(name="priority")
def priority_cmd():
    """Manage stash priorities."""


@priority_cmd.command(name="set")
@click.argument("name")
@click.argument("level", type=int)
def set_cmd(name: str, level: int):
    """Set priority LEVEL (1-10) for stash NAME."""
    try:
        set_priority(name, level)
        click.echo(f"Priority for '{name}' set to {level}.")
    except StashNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except InvalidPriorityError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@priority_cmd.command(name="get")
@click.argument("name")
def get_cmd(name: str):
    """Get the priority of stash NAME."""
    level = get_priority(name)
    marker = " (default)" if level == DEFAULT_PRIORITY else ""
    click.echo(f"{name}: {level}{marker}")


@priority_cmd.command(name="remove")
@click.argument("name")
def remove_cmd(name: str):
    """Remove explicit priority for stash NAME (resets to default)."""
    removed = remove_priority(name)
    if removed:
        click.echo(f"Priority for '{name}' removed (reset to default {DEFAULT_PRIORITY}).")
    else:
        click.echo(f"No explicit priority set for '{name}'.")


@priority_cmd.command(name="list")
@click.option("--all", "show_all", is_flag=True, help="Include stashes with default priority.")
def list_cmd(show_all: bool):
    """List stash priorities."""
    stashes = load_stashes()
    priorities = load_priorities()
    names = rank_by_priority(list(stashes.keys()))
    for name in names:
        level = priorities.get(name, DEFAULT_PRIORITY)
        if not show_all and name not in priorities:
            continue
        click.echo(f"{name}: {level}")
