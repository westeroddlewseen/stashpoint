"""Main CLI entry point for stashpoint."""

import click
from stashpoint.storage import save_stash, load_stash, load_stashes, delete_stash
from stashpoint.export import export_variables
from stashpoint.cli_export import export_cmd
from stashpoint.cli_diff import diff_cmd
from stashpoint.cli_merge import merge_cmd
from stashpoint.cli_template import template_cmd
from stashpoint.cli_history import history_cmd
from stashpoint.history import record_event


@click.group()
def cli():
    """Stashpoint — save and restore named sets of environment variables."""
    pass


@cli.command()
@click.argument("name")
@click.argument("variables", nargs=-1, required=True)
def save(name, variables):
    """Save a named stash of environment variables."""
    parsed = {}
    for var in variables:
        if "=" not in var:
            raise click.BadParameter(f"Invalid format '{var}', expected KEY=VALUE")
        key, _, value = var.partition("=")
        parsed[key] = value
    save_stash(name, parsed)
    record_event("save", name, parsed)
    click.echo(f"Stash '{name}' saved with {len(parsed)} variable(s).")


@cli.command()
@click.argument("name")
@click.option("--shell", default="bash", type=click.Choice(["bash", "fish", "powershell", "dotenv"]), show_default=True)
def load(name, shell):
    """Load a stash and print export statements."""
    variables = load_stash(name)
    if variables is None:
        raise click.ClickException(f"Stash '{name}' not found.")
    record_event("load", name, variables)
    click.echo(export_variables(variables, shell))


@cli.command(name="list")
def list_cmd():
    """List all saved stashes."""
    stashes = load_stashes()
    if not stashes:
        click.echo("No stashes saved.")
        return
    for name, variables in sorted(stashes.items()):
        click.echo(f"{name} ({len(variables)} var(s))")


@cli.command()
@click.argument("name")
def delete(name):
    """Delete a named stash."""
    if not delete_stash(name):
        raise click.ClickException(f"Stash '{name}' not found.")
    record_event("delete", name)
    click.echo(f"Stash '{name}' deleted.")


cli.add_command(export_cmd)
cli.add_command(diff_cmd)
cli.add_command(merge_cmd)
cli.add_command(template_cmd)
cli.add_command(history_cmd)
