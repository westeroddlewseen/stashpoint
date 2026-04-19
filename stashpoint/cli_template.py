"""CLI commands for template support."""

import click
from stashpoint.template import (
    list_templates,
    get_template,
    apply_template,
    TemplateNotFoundError,
)
from stashpoint.storage import save_stash, load_stash


@click.group("template")
def template_cmd():
    """Manage and apply stash templates."""


@template_cmd.command("list")
def list_cmd():
    """List all available built-in templates."""
    templates = list_templates()
    if not templates:
        click.echo("No templates available.")
        return
    click.echo("Available templates:")
    for name in templates:
        click.echo(f"  {name}")


@template_cmd.command("show")
@click.argument("template_name")
def show_cmd(template_name):
    """Show variables defined in a template."""
    try:
        variables = get_template(template_name)
    except TemplateNotFoundError as e:
        raise click.ClickException(str(e))
    click.echo(f"Template '{template_name}':")
    for key, value in sorted(variables.items()):
        click.echo(f"  {key}={value}")


@template_cmd.command("apply")
@click.argument("template_name")
@click.argument("stash_name")
@click.option("--set", "overrides", multiple=True, metavar="KEY=VALUE",
              help="Override template variables.")
@click.option("--overwrite", is_flag=True, help="Overwrite existing stash.")
def apply_cmd(template_name, stash_name, overrides, overwrite):
    """Create a stash from a template, optionally overriding variables."""
    parsed: dict = {}
    for item in overrides:
        if "=" not in item:
            raise click.ClickException(f"Invalid format '{item}'. Use KEY=VALUE.")
        key, _, value = item.partition("=")
        parsed[key.strip()] = value.strip()

    try:
        variables = apply_template(template_name, parsed)
    except TemplateNotFoundError as e:
        raise click.ClickException(str(e))

    existing = load_stash(stash_name)
    if existing is not None and not overwrite:
        raise click.ClickException(
            f"Stash '{stash_name}' already exists. Use --overwrite to replace it."
        )

    save_stash(stash_name, variables)
    click.echo(f"Stash '{stash_name}' created from template '{template_name}'.")
