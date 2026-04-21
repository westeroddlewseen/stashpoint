"""CLI commands for managing stash aliases."""

import click
from stashpoint.alias import (
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    AliasNotFoundError,
    AliasAlreadyExistsError,
    AliasTargetNotFoundError,
)


@click.group("alias")
def alias_cmd():
    """Manage stash aliases."""


@alias_cmd.command("add")
@click.argument("alias")
@click.argument("target")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing alias.")
def add_cmd(alias, target, overwrite):
    """Create ALIAS pointing to TARGET stash."""
    try:
        add_alias(alias, target, overwrite=overwrite)
        click.echo(f"Alias '{alias}' -> '{target}' created.")
    except AliasAlreadyExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except AliasTargetNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@alias_cmd.command("remove")
@click.argument("alias")
def remove_cmd(alias):
    """Remove an alias."""
    try:
        remove_alias(alias)
        click.echo(f"Alias '{alias}' removed.")
    except AliasNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@alias_cmd.command("resolve")
@click.argument("alias")
def resolve_cmd(alias):
    """Show which stash ALIAS points to."""
    try:
        target = resolve_alias(alias)
        click.echo(target)
    except AliasNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@alias_cmd.command("list")
def list_cmd():
    """List all aliases."""
    aliases = list_aliases()
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, target in sorted(aliases.items()):
        click.echo(f"{alias} -> {target}")
