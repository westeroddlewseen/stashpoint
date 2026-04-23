"""CLI commands for stash group management."""

import click
from stashpoint.group import (
    GroupNotFoundError,
    GroupAlreadyExistsError,
    create_group,
    delete_group,
    add_stash_to_group,
    remove_stash_from_group,
    get_group_members,
    list_groups,
)


@click.group("group")
def group_cmd():
    """Manage stash groups."""


@group_cmd.command("create")
@click.argument("name")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite if exists.")
def create_cmd(name, overwrite):
    """Create a new stash group."""
    try:
        create_group(name, overwrite=overwrite)
        click.echo(f"Group '{name}' created.")
    except GroupAlreadyExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@group_cmd.command("delete")
@click.argument("name")
def delete_cmd(name):
    """Delete a stash group."""
    try:
        delete_group(name)
        click.echo(f"Group '{name}' deleted.")
    except GroupNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@group_cmd.command("add")
@click.argument("group")
@click.argument("stash")
def add_cmd(group, stash):
    """Add a stash to a group."""
    try:
        add_stash_to_group(group, stash)
        click.echo(f"Added '{stash}' to group '{group}'.")
    except GroupNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@group_cmd.command("remove")
@click.argument("group")
@click.argument("stash")
def remove_cmd(group, stash):
    """Remove a stash from a group."""
    try:
        remove_stash_from_group(group, stash)
        click.echo(f"Removed '{stash}' from group '{group}'.")
    except GroupNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@group_cmd.command("show")
@click.argument("name")
def show_cmd(name):
    """Show members of a group."""
    try:
        members = get_group_members(name)
        if not members:
            click.echo(f"Group '{name}' is empty.")
        else:
            for stash in members:
                click.echo(stash)
    except GroupNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@group_cmd.command("list")
def list_cmd():
    """List all groups."""
    groups = list_groups()
    if not groups:
        click.echo("No groups defined.")
    else:
        for g in groups:
            click.echo(g)
