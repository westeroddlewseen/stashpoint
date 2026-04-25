"""CLI commands for managing favorite stashes."""

import click
from stashpoint.favorite import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
    StashNotFoundError,
    AlreadyFavoritedError,
)
from stashpoint.storage import load_stashes


@click.group("favorite")
def favorite_cmd():
    """Mark and manage favorite stashes."""


@favorite_cmd.command("add")
@click.argument("name")
@click.option("--overwrite", is_flag=True, help="Re-add if already favorited.")
def add_cmd(name: str, overwrite: bool):
    """Add a stash to favorites."""
    stashes = load_stashes()
    try:
        add_favorite(name, stashes, overwrite=overwrite)
        click.echo(f"Added '{name}' to favorites.")
    except StashNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except AlreadyFavoritedError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@favorite_cmd.command("remove")
@click.argument("name")
def remove_cmd(name: str):
    """Remove a stash from favorites."""
    removed = remove_favorite(name)
    if removed:
        click.echo(f"Removed '{name}' from favorites.")
    else:
        click.echo(f"'{name}' is not in favorites.", err=True)
        raise SystemExit(1)


@favorite_cmd.command("list")
def list_cmd():
    """List all favorite stashes."""
    favorites = list_favorites()
    if not favorites:
        click.echo("No favorites saved.")
    else:
        for name in favorites:
            click.echo(name)


@favorite_cmd.command("check")
@click.argument("name")
def check_cmd(name: str):
    """Check whether a stash is a favorite."""
    if is_favorite(name):
        click.echo(f"'{name}' is a favorite.")
    else:
        click.echo(f"'{name}' is not a favorite.")
