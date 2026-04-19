import click

from stashpoint.tag import add_tag, remove_tag, get_tags, find_by_tag


@click.group(name="tag")
def tag_cmd():
    """Manage tags on stashes."""
    pass


@tag_cmd.command(name="add")
@click.argument("stash")
@click.argument("tag")
def add_cmd(stash: str, tag: str):
    """Add a tag to a stash."""
    add_tag(stash, tag)
    click.echo(f"Tagged '{stash}' with '{tag}'.")


@tag_cmd.command(name="remove")
@click.argument("stash")
@click.argument("tag")
def remove_cmd(stash: str, tag: str):
    """Remove a tag from a stash."""
    remove_tag(stash, tag)
    click.echo(f"Removed tag '{tag}' from '{stash}'.")


@tag_cmd.command(name="list")
@click.argument("stash")
def list_cmd(stash: str):
    """List tags for a stash."""
    tags = get_tags(stash)
    if not tags:
        click.echo(f"No tags for '{stash}'.")
    else:
        for tag in sorted(tags):
            click.echo(tag)


@tag_cmd.command(name="find")
@click.argument("tag")
def find_cmd(tag: str):
    """Find stashes with a given tag."""
    stashes = find_by_tag(tag)
    if not stashes:
        click.echo(f"No stashes found with tag '{tag}'.")
    else:
        for name in stashes:
            click.echo(name)
