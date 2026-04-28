"""CLI commands for managing stash cooldowns."""

from __future__ import annotations

import click

from stashpoint.cooldown import (
    CooldownActiveError,
    StashNotFoundError,
    check_cooldown,
    clear_cooldown,
    load_cooldowns,
    set_cooldown,
)


@click.group(name="cooldown", help="Manage write cooldowns for stashes.")
def cooldown_cmd() -> None:
    pass


@cooldown_cmd.command(name="set")
@click.argument("name")
@click.argument("seconds", type=int)
def set_cmd(name: str, seconds: int) -> None:
    """Set a cooldown of SECONDS for stash NAME."""
    try:
        set_cooldown(name, seconds)
        click.echo(f"Cooldown of {seconds}s set for '{name}'.")
    except StashNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cooldown_cmd.command(name="clear")
@click.argument("name")
def clear_cmd(name: str) -> None:
    """Remove the cooldown for stash NAME."""
    removed = clear_cooldown(name)
    if removed:
        click.echo(f"Cooldown cleared for '{name}'.")
    else:
        click.echo(f"No cooldown found for '{name}'.")


@cooldown_cmd.command(name="status")
@click.argument("name")
def status_cmd(name: str) -> None:
    """Show remaining cooldown time for stash NAME."""
    remaining = check_cooldown(name)
    if remaining is None:
        click.echo(f"'{name}' has no active cooldown.")
    else:
        click.echo(f"'{name}' is on cooldown for {remaining:.1f} more second(s).")


@cooldown_cmd.command(name="list")
def list_cmd() -> None:
    """List all stashes with a configured cooldown."""
    data = load_cooldowns()
    if not data:
        click.echo("No cooldowns configured.")
        return
    for stash_name, entry in sorted(data.items()):
        interval = entry["interval"]
        last = entry.get("last_write")
        last_str = f"{last:.0f}" if last else "never"
        click.echo(f"{stash_name}: interval={interval}s  last_write={last_str}")
