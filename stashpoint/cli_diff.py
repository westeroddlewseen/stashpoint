"""CLI command for diffing two stashes."""
import click
from stashpoint.storage import load_stash
from stashpoint.diff import diff_stashes, format_diff


@click.command(name="diff")
@click.argument("stash_a")
@click.argument("stash_b")
def diff_cmd(stash_a: str, stash_b: str):
    """Show differences between two stashes."""
    vars_a = load_stash(stash_a)
    if vars_a is None:
        raise click.ClickException(f"Stash '{stash_a}' not found.")

    vars_b = load_stash(stash_b)
    if vars_b is None:
        raise click.ClickException(f"Stash '{stash_b}' not found.")

    diffs = diff_stashes(vars_a, vars_b)
    lines = format_diff(diffs, stash_a, stash_b)
    for line in lines:
        click.echo(line)
