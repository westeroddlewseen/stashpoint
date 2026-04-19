"""CLI commands for stash history."""

import click
from stashpoint.history import load_history, get_stash_history, clear_history


@click.group(name="history")
def history_cmd():
    """View and manage stash operation history."""
    pass


@history_cmd.command(name="list")
@click.option("--stash", default=None, help="Filter history by stash name.")
@click.option("--limit", default=20, show_default=True, help="Max number of entries to show.")
def list_cmd(stash, limit):
    """List recent stash history events."""
    if stash:
        entries = get_stash_history(stash)
    else:
        entries = load_history()

    entries = entries[-limit:]

    if not entries:
        click.echo("No history found.")
        return

    for entry in reversed(entries):
        var_count = len(entry.get("variables", {}))
        click.echo(
            f"[{entry['timestamp']}] {entry['action'].upper():10} {entry['stash']} ({var_count} vars)"
        )


@history_cmd.command(name="clear")
@click.confirmation_option(prompt="Are you sure you want to clear all history?")
def clear_cmd():
    """Clear all stash history."""
    clear_history()
    click.echo("History cleared.")
