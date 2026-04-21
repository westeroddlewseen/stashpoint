"""CLI command: stashpoint promote — emit shell export statements for a stash."""

import click
from stashpoint.promote import promote_stash, StashNotFoundError, UnsupportedShellError, SUPPORTED_SHELLS


@click.group(name="promote")
def promote_cmd():
    """Emit shell export statements for a stash."""


@promote_cmd.command(name="env")
@click.argument("name")
@click.option(
    "--shell",
    default="bash",
    show_default=True,
    type=click.Choice(list(SUPPORTED_SHELLS), case_sensitive=False),
    help="Target shell format.",
)
@click.option(
    "--prefix",
    default="",
    help="Prefix to prepend to every variable name.",
)
@click.option(
    "--key",
    "keys",
    multiple=True,
    help="Only promote specific keys (repeatable).",
)
def env_cmd(name: str, shell: str, prefix: str, keys: tuple):
    """Print export commands for stash NAME to stdout.

    Pipe the output to your shell's eval or source mechanism:

    \b
      eval $(stashpoint promote env myproject --shell bash)
    """
    try:
        output = promote_stash(name, shell, prefix=prefix, keys=list(keys) if keys else None)
        click.echo(output)
    except StashNotFoundError as exc:
        raise click.ClickException(str(exc))
    except UnsupportedShellError as exc:
        raise click.ClickException(str(exc))
