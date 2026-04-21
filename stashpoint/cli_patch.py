"""CLI command for patching an existing stash."""

import click
from stashpoint.patch import patch_stash, get_patch_summary, StashNotFoundError, InvalidPatchError
from stashpoint.storage import load_stash


@click.group(name="patch")
def patch_cmd():
    """Partially update an existing stash."""


@patch_cmd.command(name="apply")
@click.argument("name")
@click.option("-s", "--set", "sets", multiple=True, metavar="KEY=VALUE",
              help="Set or update a variable (can be repeated).")
@click.option("-r", "--remove", "removes", multiple=True, metavar="KEY",
              help="Remove a variable by key (can be repeated).")
@click.option("--summary", is_flag=True, default=False,
              help="Show a summary of changes made.")
def apply_cmd(name, sets, removes, summary):
    """Apply a patch to stash NAME."""
    updates = {}
    for item in sets:
        if "=" not in item:
            raise click.BadParameter(
                f"Invalid format '{item}'. Expected KEY=VALUE.",
                param_hint="--set"
            )
        key, _, value = item.partition("=")
        updates[key.strip()] = value

    remove_keys = list(removes)

    try:
        original = dict(load_stash(name) or {})
    except Exception:
        original = {}

    try:
        updated = patch_stash(name, updates, remove_keys=remove_keys)
    except StashNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except InvalidPatchError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    click.echo(f"Stash '{name}' patched successfully.")

    if summary:
        diff = get_patch_summary(original, updated)
        if diff["added"]:
            for k, v in diff["added"].items():
                click.echo(f"  + {k}={v}")
        if diff["modified"]:
            for k, vals in diff["modified"].items():
                click.echo(f"  ~ {k}: {vals['old']} -> {vals['new']}")
        if diff["removed"]:
            for k in diff["removed"]:
                click.echo(f"  - {k}")
        if not any(diff.values()):
            click.echo("  (no changes)")
