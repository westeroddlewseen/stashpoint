"""CLI commands for stash visibility management."""

import click

from stashpoint.storage import load_stashes
from stashpoint.visibility import (
    VISIBILITY_LEVELS,
    InvalidVisibilityError,
    StashNotFoundError,
    get_visibility,
    list_by_visibility,
    remove_visibility,
    set_visibility,
)


@click.group("visibility")
def visibility_cmd():
    """Manage stash visibility (private/shared/public)."""


@visibility_cmd.command("set")
@click.argument("stash_name")
@click.argument("level", type=click.Choice(VISIBILITY_LEVELS))
def set_cmd(stash_name: str, level: str):
    """Set visibility level for a stash."""
    stashes = load_stashes()
    try:
        set_visibility(stash_name, level, stashes=stashes)
        click.echo(f"Visibility for '{stash_name}' set to '{level}'.")
    except StashNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except InvalidVisibilityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@visibility_cmd.command("get")
@click.argument("stash_name")
def get_cmd(stash_name: str):
    """Get visibility level for a stash."""
    level = get_visibility(stash_name)
    click.echo(level)


@visibility_cmd.command("remove")
@click.argument("stash_name")
def remove_cmd(stash_name: str):
    """Remove explicit visibility setting (reverts to 'private')."""
    removed = remove_visibility(stash_name)
    if removed:
        click.echo(f"Visibility setting for '{stash_name}' removed.")
    else:
        click.echo(f"No explicit visibility setting for '{stash_name}'.")


@visibility_cmd.command("list")
@click.argument("level", type=click.Choice(VISIBILITY_LEVELS))
def list_cmd(level: str):
    """List all stashes with a given visibility level."""
    names = list_by_visibility(level)
    if not names:
        click.echo(f"No stashes with visibility '{level}'.")
    else:
        for name in names:
            click.echo(name)
