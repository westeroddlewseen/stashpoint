"""CLI command for merging stashes."""

import click
from .storage import load_stashes, save_stashes
from .merge import merge_stashes, get_conflicts, StashNotFoundError


@click.command(name="merge")
@click.argument("source")
@click.argument("target")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite target values with source values on conflict.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be merged without making changes.",
)
def merge_cmd(source: str, target: str, overwrite: bool, dry_run: bool) -> None:
    """Merge variables from SOURCE stash into TARGET stash."""
    stashes = load_stashes()

    try:
        conflicts = get_conflicts(stashes, source, target)

        if conflicts and not overwrite:
            click.echo(f"Conflicts found between '{source}' and '{target}':")
            for key, (tval, sval) in conflicts.items():
                click.echo(f"  {key}: '{tval}' (target) vs '{sval}' (source)")
            click.echo("Use --overwrite to resolve conflicts in favour of source.")
            raise SystemExit(1)

        merged = merge_stashes(stashes, source, target, overwrite=overwrite)

        if dry_run:
            click.echo(f"[dry-run] Result of merging '{source}' into '{target}':")
            for key, value in sorted(merged.items()):
                click.echo(f"  {key}={value}")
            return

        stashes[target] = merged
        save_stashes(stashes)
        click.echo(f"Merged '{source}' into '{target}' ({len(merged)} variables).")

    except StashNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
