import click
from stashpoint.storage import save_stash, load_stash, list_stashes, delete_stash


@click.group()
def cli():
    """Stashpoint — save and restore named sets of environment variables."""
    pass


@cli.command("save")
@click.argument("name")
@click.option("--var", "-v", multiple=True, metavar="KEY=VALUE",
              help="Environment variable to stash (KEY=VALUE). Can be repeated.")
def save(name, var):
    """Save a named stash of environment variables."""
    if not var:
        raise click.UsageError("Provide at least one variable with -v KEY=VALUE")

    env_vars = {}
    for item in var:
        if "=" not in item:
            raise click.BadParameter(f"Invalid format '{item}', expected KEY=VALUE")
        key, _, value = item.partition("=")
        env_vars[key.strip()] = value.strip()

    save_stash(name, env_vars)
    click.echo(f"Stash '{name}' saved with {len(env_vars)} variable(s).")


@cli.command("load")
@click.argument("name")
@click.option("--shell", default="bash", show_default=True,
              type=click.Choice(["bash", "fish", "json"]),
              help="Output format for the environment variables.")
def load(name, shell):
    """Print export commands for a named stash."""
    env_vars = load_stash(name)
    if env_vars is None:
        raise click.ClickException(f"Stash '{name}' not found.")

    if shell == "json":
        import json
        click.echo(json.dumps(env_vars, indent=2))
    elif shell == "fish":
        for key, value in env_vars.items():
            click.echo(f"set -x {key} '{value}';")
    else:
        for key, value in env_vars.items():
            click.echo(f"export {key}='{value}'")


@cli.command("list")
def list_cmd():
    """List all saved stashes."""
    stashes = list_stashes()
    if not stashes:
        click.echo("No stashes saved yet.")
        return
    for name in sorted(stashes):
        click.echo(f"  {name}")


@cli.command("delete")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this stash?")
def delete(name):
    """Delete a named stash."""
    removed = delete_stash(name)
    if not removed:
        raise click.ClickException(f"Stash '{name}' not found.")
    click.echo(f"Stash '{name}' deleted.")


if __name__ == "__main__":
    cli()
