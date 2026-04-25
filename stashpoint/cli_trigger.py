"""CLI commands for managing directory-based stash triggers."""

import click
from stashpoint.trigger import (
    TriggerNotFoundError,
    register_trigger,
    unregister_trigger,
    get_trigger,
    list_triggers,
)


@click.group("trigger")
def trigger_cmd():
    """Manage directory-based stash triggers."""


@trigger_cmd.command("add")
@click.argument("directory")
@click.argument("stash")
@click.option(
    "--event",
    type=click.Choice(["enter", "leave"]),
    default="enter",
    show_default=True,
    help="When to activate the stash.",
)
def add_cmd(directory, stash, event):
    """Register STASH to load when entering/leaving DIRECTORY."""
    try:
        register_trigger(directory, stash, event)
        click.echo(f"Trigger registered: [{event}] {directory} -> {stash}")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@trigger_cmd.command("remove")
@click.argument("directory")
@click.option(
    "--event",
    type=click.Choice(["enter", "leave"]),
    default=None,
    help="Remove only this event (default: remove all).",
)
def remove_cmd(directory, event):
    """Remove a trigger for DIRECTORY."""
    try:
        unregister_trigger(directory, event)
        click.echo(f"Trigger removed for {directory}")
    except TriggerNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@trigger_cmd.command("list")
def list_cmd():
    """List all registered triggers."""
    entries = list_triggers()
    if not entries:
        click.echo("No triggers registered.")
        return
    for entry in entries:
        click.echo(f"[{entry['event']}] {entry['directory']} -> {entry['stash']}")


@trigger_cmd.command("check")
@click.argument("directory")
@click.option("--event", type=click.Choice(["enter", "leave"]), default="enter", show_default=True)
def check_cmd(directory, event):
    """Show which stash would activate for DIRECTORY and EVENT."""
    stash = get_trigger(directory, event)
    if stash:
        click.echo(stash)
    else:
        click.echo(f"No trigger for [{event}] {directory}")
        raise SystemExit(1)
