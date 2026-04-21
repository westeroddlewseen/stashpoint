"""CLI commands for archiving and restoring stashes."""

import click

from stashpoint.archive import (
    ArchiveError,
    StashNotFoundError,
    create_archive,
    restore_archive,
)


@click.group("archive")
def archive_cmd():
    """Archive stashes to or from a portable ZIP file."""


@archive_cmd.command("create")
@click.argument("names", nargs=-1, required=True)
@click.option("-o", "--output", required=True, help="Destination ZIP file path.")
def create_cmd(names, output):
    """Export one or more stashes into a ZIP archive."""
    try:
        result = create_archive(list(names), output)
    except StashNotFoundError as exc:
        raise click.ClickException(str(exc))
    except ArchiveError as exc:
        raise click.ClickException(str(exc))

    click.echo(f"Archived {len(result['archived'])} stash(es) to {result['path']}")
    for name in result["archived"]:
        click.echo(f"  + {name}")


@archive_cmd.command("restore")
@click.argument("path")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing stashes with the same name.",
)
def restore_cmd(path, overwrite):
    """Import stashes from a ZIP archive."""
    try:
        result = restore_archive(path, overwrite=overwrite)
    except ArchiveError as exc:
        raise click.ClickException(str(exc))

    if result["restored"]:
        click.echo(f"Restored {len(result['restored'])} stash(es):")
        for name in result["restored"]:
            click.echo(f"  + {name}")

    if result["skipped"]:
        click.echo(f"Skipped {len(result['skipped'])} stash(es) (already exist):")
        for name in result["skipped"]:
            click.echo(f"  ~ {name}")

    if not result["restored"] and not result["skipped"]:
        click.echo("Archive contained no stashes.")
