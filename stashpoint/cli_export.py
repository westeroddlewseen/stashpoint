"""CLI command for exporting stashes to files or stdout."""

import click
from pathlib import Path

from stashpoint.storage import load_stash, StashNotFoundError
from stashpoint.export import export_variables, SUPPORTED_SHELLS


@click.command("export")
@click.argument("name")
@click.option(
    "--shell",
    "-s",
    default="bash",
    show_default=True,
    type=click.Choice(["bash", "zsh", "fish", "powershell", "dotenv"], case_sensitive=False),
    help="Output format for the exported variables.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(dir_okay=False, writable=True),
    help="Write output to a file instead of stdout.",
)
def export_cmd(name: str, shell: str, output: str) -> None:
    """Export a stash's variables in the specified shell format.

    NAME is the stash to export.
    """
    try:
        variables = load_stash(name)
    except StashNotFoundError:
        click.echo(f"Error: stash '{name}' not found.", err=True)
        raise click.exceptions.Exit(1)

    try:
        content = export_variables(variables, shell)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise click.exceptions.Exit(1)

    if output:
        path = Path(output)
        path.write_text(content + "\n", encoding="utf-8")
        click.echo(f"Exported stash '{name}' to {path} ({shell} format).")
    else:
        click.echo(content)
