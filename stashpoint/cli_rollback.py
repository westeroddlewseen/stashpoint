"""CLI commands for rolling back stashes to previous states."""

import click
from stashpoint.rollback import (
    list_rollback_points,
    rollback_stash,
    get_rollback_summary,
    StashNotFoundError,
    RollbackPointNotFoundError,
)


@click.group(name="rollback")
def rollback_cmd():
    """Roll back a stash to a previous saved state."""


@rollback_cmd.command(name="list")
@click.argument("stash_name")
def list_cmd(stash_name):
    """List available rollback points for a stash."""
    click.echo(get_rollback_summary(stash_name))


@rollback_cmd.command(name="apply")
@click.argument("stash_name")
@click.argument("index", type=int, default=0)
@click.option("--force", is_flag=True, default=False, help="Overwrite current stash.")
def apply_cmd(stash_name, index, force):
    """Restore STASH_NAME to rollback point INDEX (default: 0, most recent)."""
    try:
        restored = rollback_stash(stash_name, index, overwrite=True)
        click.echo(
            f"Rolled back '{stash_name}' to point [{index}] "
            f"({len(restored)} variable(s) restored)."
        )
    except StashNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except RollbackPointNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
