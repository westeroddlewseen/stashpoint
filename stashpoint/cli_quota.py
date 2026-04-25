"""CLI commands for managing stashpoint quotas."""

import click

from stashpoint.quota import (
    clear_quota,
    get_quota_status,
    set_quota,
)


@click.group(name="quota")
def quota_cmd():
    """Manage stash quota limits."""


@quota_cmd.command(name="set")
@click.option("--max-stashes", type=int, default=None, help="Maximum number of stashes allowed.")
@click.option("--max-vars", type=int, default=None, help="Maximum variables per stash.")
def set_cmd(max_stashes, max_vars):
    """Set quota limits."""
    if max_stashes is None and max_vars is None:
        raise click.UsageError("Provide at least --max-stashes or --max-vars.")
    try:
        quota = set_quota(max_stashes=max_stashes, max_vars_per_stash=max_vars)
    except ValueError as exc:
        raise click.ClickException(str(exc))
    if max_stashes is not None:
        click.echo(f"Max stashes set to {quota['max_stashes']}.")
    if max_vars is not None:
        click.echo(f"Max vars per stash set to {quota['max_vars_per_stash']}.")


@quota_cmd.command(name="clear")
def clear_cmd():
    """Remove all quota limits."""
    clear_quota()
    click.echo("All quota limits cleared.")


@quota_cmd.command(name="status")
def status_cmd():
    """Show current quota settings and usage."""
    status = get_quota_status()
    stash_limit = status["max_stashes"]
    var_limit = status["max_vars_per_stash"]
    current = status["current_stashes"]

    stash_limit_str = str(stash_limit) if stash_limit is not None else "unlimited"
    var_limit_str = str(var_limit) if var_limit is not None else "unlimited"

    click.echo(f"Stashes:          {current} / {stash_limit_str}")
    click.echo(f"Vars per stash:   {var_limit_str}")
