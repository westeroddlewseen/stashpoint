"""CLI commands for managing stash expiry."""

from __future__ import annotations

import time

import click

from stashpoint.expire import (
    StashNotFoundError,
    clear_expiry,
    get_expiry,
    is_expired,
    purge_expired,
    set_expiry,
)


@click.group(name="expire")
def expire_cmd():
    """Manage stash expiry / TTL."""


@expire_cmd.command(name="set")
@click.argument("name")
@click.option("--ttl", required=True, type=float, help="Time-to-live in seconds.")
def set_cmd(name: str, ttl: float):
    """Set a TTL on a stash."""
    try:
        expires_at = set_expiry(name, ttl)
        formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires_at))
        click.echo(f"Stash '{name}' will expire at {formatted}.")
    except StashNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@expire_cmd.command(name="clear")
@click.argument("name")
def clear_cmd(name: str):
    """Remove the expiry from a stash."""
    removed = clear_expiry(name)
    if removed:
        click.echo(f"Expiry cleared for stash '{name}'.")
    else:
        click.echo(f"No expiry was set for stash '{name}'.")


@expire_cmd.command(name="status")
@click.argument("name")
def status_cmd(name: str):
    """Show expiry status for a stash."""
    ts = get_expiry(name)
    if ts is None:
        click.echo(f"Stash '{name}' has no expiry set.")
        return
    formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
    expired = is_expired(name)
    state = "EXPIRED" if expired else "active"
    click.echo(f"Stash '{name}': expires {formatted} [{state}]")


@expire_cmd.command(name="purge")
def purge_cmd():
    """Delete all expired stashes."""
    purged = purge_expired()
    if purged:
        for name in purged:
            click.echo(f"Purged: {name}")
        click.echo(f"{len(purged)} stash(es) purged.")
    else:
        click.echo("No expired stashes found.")
