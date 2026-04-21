"""CLI command for watching a stash for changes."""

import click

from stashpoint.watch import poll_stash, get_changes, StashNotFoundError


@click.group(name="watch")
def watch_cmd():
    """Watch a stash for changes."""


@watch_cmd.command(name="start")
@click.argument("name")
@click.option("--interval", default=2.0, show_default=True, help="Poll interval in seconds.")
@click.option("--limit", default=None, type=int, help="Stop after N change events detected.")
@click.option("--quiet", is_flag=True, help="Suppress change output; only print stash name on change.")
def start_cmd(name: str, interval: float, limit: int, quiet: bool):
    """Watch stash NAME and print changes as they occur."""
    change_count = 0

    def on_change(stash_name, old_vars, new_vars):
        nonlocal change_count
        change_count += 1
        summary = get_changes(old_vars, new_vars)

        if quiet:
            click.echo(stash_name)
            return

        click.echo(f"[change #{change_count}] stash '{stash_name}' updated")
        for k, v in summary["added"].items():
            click.echo(f"  + {k}={v}")
        for k in summary["removed"]:
            click.echo(f"  - {k}")
        for k, (old, new) in summary["changed"].items():
            click.echo(f"  ~ {k}: {old!r} -> {new!r}")

    try:
        max_polls = None if limit is None else limit * 1000
        poll_stash(
            name,
            interval=interval,
            max_polls=max_polls,
            on_change=on_change,
        )
    except StashNotFoundError as e:
        raise click.ClickException(str(e))
    except KeyboardInterrupt:
        click.echo("\nWatch stopped.")
