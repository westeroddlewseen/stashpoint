"""CLI commands for stash locking."""

import click
from stashpoint.lock import lock_stash, unlock_stash, is_locked, load_locks


@click.group("lock")
def lock_cmd():
    """Lock or unlock stashes to prevent modification."""


@lock_cmd.command("add")
@click.argument("name")
def add_cmd(name: str):
    """Lock a stash by name."""
    if is_locked(name):
        click.echo(f"Stash '{name}' is already locked.")
        return
    lock_stash(name)
    click.echo(f"Stash '{name}' locked.")


@lock_cmd.command("remove")
@click.argument("name")
def remove_cmd(name: str):
    """Unlock a stash by name."""
    if not is_locked(name):
        click.echo(f"Stash '{name}' is not locked.")
        return
    unlock_stash(name)
    click.echo(f"Stash '{name}' unlocked.")


@lock_cmd.command("list")
def list_cmd():
    """List all locked stashes."""
    locks = load_locks()
    if not locks:
        click.echo("No locked stashes.")
        return
    for name in sorted(locks):
        click.echo(f"  🔒 {name}")
