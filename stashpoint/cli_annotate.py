"""CLI commands for managing stash annotations."""

import click
from stashpoint.annotate import (
    set_annotation,
    get_annotation,
    remove_annotation,
    list_annotations,
    StashNotFoundError,
)
from stashpoint.storage import load_stashes


@click.group("annotate")
def annotate_cmd():
    """Add or view notes on stashes."""


@annotate_cmd.command("set")
@click.argument("stash_name")
@click.argument("note")
def set_cmd(stash_name, note):
    """Set or update the annotation for STASH_NAME."""
    stashes = load_stashes()
    try:
        set_annotation(stash_name, note, stashes=stashes)
        click.echo(f"Annotation set for '{stash_name}'.")
    except StashNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@annotate_cmd.command("get")
@click.argument("stash_name")
def get_cmd(stash_name):
    """Show the annotation for STASH_NAME."""
    note = get_annotation(stash_name)
    if note is None:
        click.echo(f"No annotation for '{stash_name}'.")
    else:
        click.echo(note)


@annotate_cmd.command("remove")
@click.argument("stash_name")
def remove_cmd(stash_name):
    """Remove the annotation for STASH_NAME."""
    removed = remove_annotation(stash_name)
    if removed:
        click.echo(f"Annotation removed for '{stash_name}'.")
    else:
        click.echo(f"No annotation found for '{stash_name}'.")


@annotate_cmd.command("list")
def list_cmd():
    """List all annotated stashes."""
    annotations = list_annotations()
    if not annotations:
        click.echo("No annotations found.")
        return
    for name, note in sorted(annotations.items()):
        click.echo(f"{name}: {note}")
