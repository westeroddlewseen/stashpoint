"""CLI commands for the stash rating feature."""

import click

from stashpoint.rating import (
    InvalidRatingError,
    StashNotFoundError,
    get_rating,
    get_top_rated,
    rate_stash,
    remove_rating,
)


@click.group(name="rating")
def rating_cmd():
    """Rate stashes with a 1-5 star score."""


@rating_cmd.command(name="set")
@click.argument("name")
@click.argument("stars", type=int)
def set_cmd(name: str, stars: int):
    """Assign a STARS rating (1-5) to stash NAME."""
    try:
        rate_stash(name, stars)
        click.echo(f"Rated '{name}': {'★' * stars}{'☆' * (5 - stars)} ({stars}/5)")
    except StashNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except InvalidRatingError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@rating_cmd.command(name="get")
@click.argument("name")
def get_cmd(name: str):
    """Show the rating for stash NAME."""
    rating = get_rating(name)
    if rating is None:
        click.echo(f"'{name}' has not been rated.")
    else:
        click.echo(f"'{name}': {'★' * rating}{'☆' * (5 - rating)} ({rating}/5)")


@rating_cmd.command(name="remove")
@click.argument("name")
def remove_cmd(name: str):
    """Remove the rating for stash NAME."""
    removed = remove_rating(name)
    if removed:
        click.echo(f"Rating removed for '{name}'.")
    else:
        click.echo(f"'{name}' had no rating to remove.")


@rating_cmd.command(name="top")
@click.option("--limit", "-n", default=10, show_default=True, help="Number of results.")
def top_cmd(limit: int):
    """List the top-rated stashes."""
    results = get_top_rated(limit)
    if not results:
        click.echo("No stashes have been rated yet.")
        return
    for stash_name, stars in results:
        bar = '★' * stars + '☆' * (5 - stars)
        click.echo(f"{bar}  {stash_name}")
