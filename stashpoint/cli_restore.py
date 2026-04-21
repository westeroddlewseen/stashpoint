"""CLI commands for restoring stashes to the current shell environment."""

import click
from .restore import restore_stash, write_restore_script, StashNotFoundError, StashLockedError, UnsupportedShellError


@click.group(name="restore")
def restore_cmd():
    """Restore a stash to the current shell environment."""
    pass


@restore_cmd.command(name="shell")
@click.argument("name")
@click.option(
    "--shell",
    "shell_type",
    type=click.Choice(["bash", "zsh", "fish", "powershell"], case_sensitive=False),
    default="bash",
    show_default=True,
    help="Target shell format for the restore script.",
)
@click.option(
    "--prefix",
    default=None,
    help="Only restore variables with this prefix.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print the restore script without writing to disk.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(),
    help="Write the restore script to this file instead of stdout.",
)
def shell_cmd(name, shell_type, prefix, dry_run, output):
    """Generate a shell script to restore a named stash.

    Outputs export statements suitable for sourcing in the target shell.
    Use --output to write the script to a file, or pipe stdout directly.

    Example:
        eval $(stashpoint restore shell myproject --shell bash)
    """
    try:
        script = restore_stash(name, shell=shell_type, prefix=prefix)
    except StashNotFoundError:
        raise click.ClickException(f"Stash '{name}' not found.")
    except StashLockedError:
        raise click.ClickException(
            f"Stash '{name}' is locked and cannot be restored."
        )
    except UnsupportedShellError as e:
        raise click.ClickException(str(e))

    if dry_run:
        click.echo(script)
        return

    if output:
        try:
            write_restore_script(script, output)
            click.echo(f"Restore script written to '{output}'.")
        except OSError as e:
            raise click.ClickException(f"Could not write file: {e}")
    else:
        click.echo(script)


@restore_cmd.command(name="env")
@click.argument("name")
@click.option(
    "--prefix",
    default=None,
    help="Only restore variables with this prefix.",
)
def env_cmd(name, prefix):
    """Print key=value pairs from a stash (dotenv format).

    Useful for tools that accept dotenv-style input or for inspection.

    Example:
        stashpoint restore env myproject
    """
    try:
        script = restore_stash(name, shell="dotenv", prefix=prefix)
    except StashNotFoundError:
        raise click.ClickException(f"Stash '{name}' not found.")
    except StashLockedError:
        raise click.ClickException(
            f"Stash '{name}' is locked and cannot be restored."
        )
    except UnsupportedShellError as e:
        raise click.ClickException(str(e))

    click.echo(script)
