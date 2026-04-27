"""CLI commands for the badge feature."""

import click
from stashpoint.badge import (
    compute_badges,
    format_badges,
    BADGE_DEFINITIONS,
    StashNotFoundError,
)


@click.group(name="badge")
def badge_cmd():
    """View badges earned by stashes."""


@badge_cmd.command(name="show")
@click.argument("stash_name")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def show_cmd(stash_name: str, as_json: bool):
    """Show badges earned by STASH_NAME."""
    try:
        result = compute_badges(stash_name)
    except StashNotFoundError as exc:
        raise click.ClickException(str(exc))

    if as_json:
        import json
        click.echo(json.dumps({"stash": result.stash_name, "badges": result.badges}))
    else:
        click.echo(format_badges(result))


@badge_cmd.command(name="list-all")
def list_all_cmd():
    """List all available badge definitions."""
    click.echo("Available badges:")
    for key, description in BADGE_DEFINITIONS.items():
        click.echo(f"  {description}")


@badge_cmd.command(name="check")
@click.argument("stash_name")
@click.argument("badge_name")
def check_cmd(stash_name: str, badge_name: str):
    """Check whether STASH_NAME has earned BADGE_NAME."""
    if badge_name not in BADGE_DEFINITIONS:
        raise click.ClickException(
            f"Unknown badge '{badge_name}'. Run 'badge list-all' to see available badges."
        )
    try:
        result = compute_badges(stash_name)
    except StashNotFoundError as exc:
        raise click.ClickException(str(exc))

    if badge_name in result.badges:
        click.echo(f"✓ '{stash_name}' has earned the '{badge_name}' badge.")
    else:
        click.echo(f"✗ '{stash_name}' has not earned the '{badge_name}' badge.")
