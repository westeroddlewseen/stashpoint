"""Main CLI entry point for stashpoint."""

import click
from stashpoint.storage import save_stash, load_stash, delete_stash, list_stashes
from stashpoint.export import export_variables
from stashpoint.cli_export import export_cmd
from stashpoint.cli_diff import diff_cmd
from stashpoint.cli_merge import merge_cmd
from stashpoint.cli_template import template_cmd


@click.group()
def cli():
    """stashpoint — save and restore named sets of environment variables."""


@cli.command()
@click.argument("name")
@click.argument("variables", nargs=-1)
def save(name, variables):
    """Save a named stash of environment variables."""
    if not variables:
        raise click.ClickException("No variables provided.")
    parsed = {}
    for var in variables:
        if "=" not in var:
            raise click.ClickException(f"Invalid variable format: '{var}'. Use KEY=VALUE.")
        key, _, value = var.partition("=")
        parsed[key.strip()] = value.strip()
    save_stash(name, parsed)
    click.echo(f"Stash '{name}' saved with {len(parsed)} variable(s).")


@cli.command()
@click.argument("name")
@click.option("--shell", default="bash",
              type=click.Choice(["bash", "fish", "powershell", "dotenv"]),
              help="Output format.")
def load(name, shell):
    """Load a stash and print export statements."""
    variables = load_stash(name)
    if variables is None:
        raise click.ClickException(f"Stash '{name}' not found.")
    click.echo(export_variables(variables, shell))


@cli.command("list")
def list_cmd():
    """List all saved stashes."""
    stashes = list_stashes()
    if not stashes:
        click.echo("No stashes saved.")
        return
    click.echo("Saved stashes:")
    for name in stashes:
        click.echo(f"  {name}")


@cli.command()
@click.argument("name")
def delete(name):
    """Delete a named stash."""
    deleted = delete_stash(name)
    if not deleted:
        raise click.ClickException(f"Stash '{name}' not found.")
    click.echo(f"Stash '{name}' deleted.")


cli.add_command(export_cmd, "export")
cli.add_command(diff_cmd, "diff")
cli.add_command(merge_cmd, "merge")
cli.add_command(template_cmd, "template")
