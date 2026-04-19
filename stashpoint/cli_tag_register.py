"""Helper to register tag_cmd into the main CLI."""


def register(cli):
    from stashpoint.cli_tag import tag_cmd
    cli.add_command(tag_cmd)
