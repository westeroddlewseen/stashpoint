"""CLI commands for pin management."""

import click
from stashpoint.pin import pin_stash, unpin_stash, list_pinned, is_pinned


@click.group(name="pin")
def pin_cmd():
    """Manage pinned stashes."""


@pin_cmd.command(name="add")
@click.argument("name")
def add_cmd(name: str):
    """Pin a stash to protect it from deletion."""
    if is_pinned(name):
        click.echo(f"Stash '{name}' is already pinned.")
        return
    pin_stash(name)
    click.echo(f"Stash '{name}' pinned.")


@pin_cmd.command(name="remove")
@click.argument("name")
def remove_cmd(name: str):
    """Unpin a stash."""
    if not is_pinned(name):
        click.echo(f"Stash '{name}' is not pinned.")
        return
    unpin_stash(name)
    click.echo(f"Stash '{name}' unpinned.")


@pin_cmd.command(name="list")
def list_cmd():
    """List all pinned stashes."""
    pinned = list_pinned()
    if not pinned:
        click.echo("No pinned stashes.")
        return
    for name in pinned:
        click.echo(f"  📌 {name}")


@pin_cmd.command(name="check")
@click.argument("name")
def check_cmd(name: str):
    """Check whether a stash is pinned."""
    if is_pinned(name):
        click.echo(f"Stash '{name}' is pinned.")
    else:
        click.echo(f"Stash '{name}' is not pinned.")
