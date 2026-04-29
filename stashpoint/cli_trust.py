"""CLI commands for stash trust level management."""

import click
from stashpoint.trust import (
    TRUST_LEVELS,
    DEFAULT_TRUST,
    InvalidTrustLevelError,
    StashNotFoundError,
    set_trust,
    get_trust,
    remove_trust,
    list_trust,
)
from stashpoint.storage import load_stashes


@click.group(name="trust")
def trust_cmd():
    """Manage trust levels for stashes."""


@trust_cmd.command(name="set")
@click.argument("name")
@click.argument("level", type=click.Choice(TRUST_LEVELS))
def set_cmd(name: str, level: str):
    """Set the trust level for a stash."""
    stashes = load_stashes()
    try:
        set_trust(name, level, stashes=stashes)
        click.echo(f"Trust level for '{name}' set to '{level}'.")
    except StashNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except InvalidTrustLevelError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@trust_cmd.command(name="get")
@click.argument("name")
def get_cmd(name: str):
    """Get the trust level for a stash."""
    level = get_trust(name)
    click.echo(f"{name}: {level}")


@trust_cmd.command(name="remove")
@click.argument("name")
def remove_cmd(name: str):
    """Remove explicit trust level, reverting to default."""
    removed = remove_trust(name)
    if removed:
        click.echo(f"Trust level for '{name}' removed (reverts to '{DEFAULT_TRUST}').")
    else:
        click.echo(f"No explicit trust level set for '{name}'.")


@trust_cmd.command(name="list")
def list_cmd():
    """List all explicitly set trust levels."""
    data = list_trust()
    if not data:
        click.echo("No trust levels explicitly set.")
        return
    for stash_name, level in sorted(data.items()):
        click.echo(f"{stash_name}: {level}")
