"""CLI commands for category management."""

import click

from stashpoint.category import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    StashNotFoundError,
    add_to_category,
    create_category,
    delete_category,
    get_stash_categories,
    list_categories,
    load_categories,
    remove_from_category,
)


@click.group(name="category")
def category_cmd():
    """Manage stash categories."""


@category_cmd.command("create")
@click.argument("name")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing category.")
def create_cmd(name: str, overwrite: bool) -> None:
    """Create a new category."""
    try:
        create_category(name, overwrite=overwrite)
        click.echo(f"Category '{name}' created.")
    except CategoryAlreadyExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@category_cmd.command("delete")
@click.argument("name")
def delete_cmd(name: str) -> None:
    """Delete a category."""
    try:
        delete_category(name)
        click.echo(f"Category '{name}' deleted.")
    except CategoryNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@category_cmd.command("add")
@click.argument("category")
@click.argument("stash")
def add_cmd(category: str, stash: str) -> None:
    """Add a stash to a category."""
    try:
        add_to_category(category, stash)
        click.echo(f"Added '{stash}' to category '{category}'.")
    except (CategoryNotFoundError, StashNotFoundError) as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@category_cmd.command("remove")
@click.argument("category")
@click.argument("stash")
def remove_cmd(category: str, stash: str) -> None:
    """Remove a stash from a category."""
    try:
        remove_from_category(category, stash)
        click.echo(f"Removed '{stash}' from category '{category}'.")
    except CategoryNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@category_cmd.command("list")
def list_cmd() -> None:
    """List all categories and their members."""
    cats = load_categories()
    if not cats:
        click.echo("No categories defined.")
        return
    for name in sorted(cats):
        members = cats[name]
        member_str = ", ".join(members) if members else "(empty)"
        click.echo(f"{name}: {member_str}")


@category_cmd.command("find")
@click.argument("stash")
def find_cmd(stash: str) -> None:
    """Find which categories a stash belongs to."""
    cats = get_stash_categories(stash)
    if not cats:
        click.echo(f"'{stash}' is not in any category.")
    else:
        for cat in cats:
            click.echo(cat)
