"""CLI commands for managing stash notes."""

import click

from stashpoint.note import (
    NoteNotFoundError,
    StashNotFoundError,
    get_note,
    list_notes,
    remove_note,
    set_note,
)


@click.group("note")
def note_cmd() -> None:
    """Attach free-form notes to stashes."""


@note_cmd.command("set")
@click.argument("stash")
@click.argument("text")
def set_cmd(stash: str, text: str) -> None:
    """Attach TEXT as a note on STASH."""
    try:
        set_note(stash, text)
    except StashNotFoundError:
        raise click.ClickException(f"Stash '{stash}' not found.")
    click.echo(f"Note set for '{stash}'.")


@note_cmd.command("get")
@click.argument("stash")
def get_cmd(stash: str) -> None:
    """Print the note attached to STASH."""
    note = get_note(stash)
    if note is None:
        raise click.ClickException(f"No note found for '{stash}'.")
    click.echo(note)


@note_cmd.command("remove")
@click.argument("stash")
def remove_cmd(stash: str) -> None:
    """Remove the note attached to STASH."""
    try:
        remove_note(stash)
    except NoteNotFoundError:
        raise click.ClickException(f"No note found for '{stash}'.")
    click.echo(f"Note removed for '{stash}'.")


@note_cmd.command("list")
def list_cmd() -> None:
    """List all stashes that have notes."""
    notes = list_notes()
    if not notes:
        click.echo("No notes found.")
        return
    for name, text in sorted(notes.items()):
        click.echo(f"{name}: {text}")
