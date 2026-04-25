"""CLI commands for stash reminders."""

from __future__ import annotations

import click

from stashpoint.remind import (
    ReminderNotFoundError,
    StashNotFoundError,
    get_reminder,
    list_reminders,
    remove_reminder,
    set_reminder,
)


@click.group("remind")
def remind_cmd() -> None:
    """Manage reminders attached to stashes."""


@remind_cmd.command("set")
@click.argument("name")
@click.argument("message")
def set_cmd(name: str, message: str) -> None:
    """Attach a REMINDER MESSAGE to stash NAME."""
    try:
        set_reminder(name, message)
        click.echo(f"Reminder set for '{name}'.")
    except StashNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@remind_cmd.command("get")
@click.argument("name")
def get_cmd(name: str) -> None:
    """Show the reminder for stash NAME."""
    msg = get_reminder(name)
    if msg is None:
        click.echo(f"No reminder set for '{name}'.")
    else:
        click.echo(msg)


@remind_cmd.command("remove")
@click.argument("name")
def remove_cmd(name: str) -> None:
    """Remove the reminder for stash NAME."""
    try:
        remove_reminder(name)
        click.echo(f"Reminder removed for '{name}'.")
    except ReminderNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@remind_cmd.command("list")
def list_cmd() -> None:
    """List all stash reminders."""
    reminders = list_reminders()
    if not reminders:
        click.echo("No reminders set.")
        return
    for stash_name, message in reminders.items():
        click.echo(f"{stash_name}: {message}")
