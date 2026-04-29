"""Register category commands with the main CLI."""

from stashpoint.cli_category import category_cmd


def register(cli):
    cli.add_command(category_cmd)
