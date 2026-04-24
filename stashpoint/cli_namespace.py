"""CLI commands for namespace management."""

import click

from stashpoint.namespace import (
    NamespaceAlreadyExistsError,
    NamespaceNotFoundError,
    add_to_namespace,
    create_namespace,
    delete_namespace,
    get_namespace_stashes,
    list_namespaces,
    remove_from_namespace,
)


@click.group("namespace")
def namespace_cmd():
    """Manage stash namespaces."""


@namespace_cmd.command("create")
@click.argument("name")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite if exists.")
def create_cmd(name: str, overwrite: bool):
    """Create a new namespace."""
    try:
        create_namespace(name, overwrite=overwrite)
        click.echo(f"Namespace '{name}' created.")
    except NamespaceAlreadyExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@namespace_cmd.command("delete")
@click.argument("name")
def delete_cmd(name: str):
    """Delete a namespace."""
    try:
        delete_namespace(name)
        click.echo(f"Namespace '{name}' deleted.")
    except NamespaceNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@namespace_cmd.command("add")
@click.argument("namespace")
@click.argument("stash")
def add_cmd(namespace: str, stash: str):
    """Add a stash to a namespace."""
    try:
        add_to_namespace(namespace, stash)
        click.echo(f"Added '{stash}' to namespace '{namespace}'.")
    except NamespaceNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@namespace_cmd.command("remove")
@click.argument("namespace")
@click.argument("stash")
def remove_cmd(namespace: str, stash: str):
    """Remove a stash from a namespace."""
    try:
        remove_from_namespace(namespace, stash)
        click.echo(f"Removed '{stash}' from namespace '{namespace}'.")
    except NamespaceNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@namespace_cmd.command("list")
def list_cmd():
    """List all namespaces."""
    names = list_namespaces()
    if not names:
        click.echo("No namespaces defined.")
    else:
        for name in names:
            click.echo(name)


@namespace_cmd.command("show")
@click.argument("name")
def show_cmd(name: str):
    """Show stashes in a namespace."""
    try:
        stashes = get_namespace_stashes(name)
        if not stashes:
            click.echo(f"Namespace '{name}' is empty.")
        else:
            for s in stashes:
                click.echo(s)
    except NamespaceNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
