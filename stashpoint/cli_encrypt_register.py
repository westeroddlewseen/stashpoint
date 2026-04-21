"""Registration helper for the encrypt CLI command group."""

from stashpoint.cli_encrypt import encrypt_cmd


def register(cli):
    """Register the encrypt command group with the main CLI."""
    cli.add_command(encrypt_cmd)
