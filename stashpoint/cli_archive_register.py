"""Registration helper for the archive CLI command group."""

from stashpoint.cli_archive import archive_cmd


def register(cli):
    """Attach the archive command group to *cli*."""
    cli.add_command(archive_cmd)
