"""Register the workflow command group with the main CLI."""
from stashpoint.cli_workflow import workflow_cmd


def register(cli):
    cli.add_command(workflow_cmd)
