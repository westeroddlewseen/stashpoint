"""CLI commands for managing profiles."""

import click

from stashpoint.profile import (
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    add_stash_to_profile,
    create_profile,
    delete_profile,
    get_profile,
    load_profiles,
    remove_stash_from_profile,
)


@click.group(name="profile")
def profile_cmd():
    """Manage stash profiles (named groups of stashes)."""


@profile_cmd.command(name="create")
@click.argument("name")
@click.argument("stashes", nargs=-1)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite if exists.")
def create_cmd(name, stashes, overwrite):
    """Create a profile with optional initial stashes."""
    try:
        create_profile(name, list(stashes), overwrite=overwrite)
        click.echo(f"Profile '{name}' created with {len(stashes)} stash(es).")
    except ProfileAlreadyExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_cmd.command(name="delete")
@click.argument("name")
def delete_cmd(name):
    """Delete a profile by name."""
    try:
        delete_profile(name)
        click.echo(f"Profile '{name}' deleted.")
    except ProfileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_cmd.command(name="show")
@click.argument("name")
def show_cmd(name):
    """Show stashes in a profile."""
    try:
        stashes = get_profile(name)
        if stashes:
            click.echo(f"Profile '{name}':")
            for s in stashes:
                click.echo(f"  - {s}")
        else:
            click.echo(f"Profile '{name}' is empty.")
    except ProfileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_cmd.command(name="list")
def list_cmd():
    """List all profiles."""
    profiles = load_profiles()
    if not profiles:
        click.echo("No profiles found.")
    else:
        for name, stashes in sorted(profiles.items()):
            click.echo(f"{name} ({len(stashes)} stash(es))")


@profile_cmd.command(name="add")
@click.argument("profile")
@click.argument("stash")
def add_cmd(profile, stash):
    """Add a stash to a profile."""
    try:
        add_stash_to_profile(profile, stash)
        click.echo(f"Added '{stash}' to profile '{profile}'.")
    except ProfileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_cmd.command(name="remove")
@click.argument("profile")
@click.argument("stash")
def remove_cmd(profile, stash):
    """Remove a stash from a profile."""
    try:
        remove_stash_from_profile(profile, stash)
        click.echo(f"Removed '{stash}' from profile '{profile}'.")
    except ProfileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
