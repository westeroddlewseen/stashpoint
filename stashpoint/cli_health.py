"""CLI commands for stash health checks."""

import click
from stashpoint.health import (
    check_stash_health,
    check_all_health,
    format_health_report,
    StashNotFoundError,
)


@click.group(name="health")
def health_cmd():
    """Check the health of stashes."""


@health_cmd.command(name="check")
@click.argument("name", required=False)
@click.option("--all", "check_all", is_flag=True, help="Check all stashes.")
@click.option("--errors-only", is_flag=True, help="Only show stashes with errors.")
def check_cmd(name: str, check_all: bool, errors_only: bool):
    """Check health of a stash or all stashes."""
    if not name and not check_all:
        raise click.UsageError("Provide a stash NAME or use --all.")

    if check_all:
        reports = check_all_health()
        if not reports:
            click.echo("No stashes found.")
            return
        any_unhealthy = False
        for report in reports:
            if errors_only and report.healthy:
                continue
            click.echo(format_health_report(report))
            if not report.healthy:
                any_unhealthy = True
        if any_unhealthy:
            raise SystemExit(1)
    else:
        try:
            report = check_stash_health(name)
        except StashNotFoundError as e:
            click.echo(str(e), err=True)
            raise SystemExit(1)
        click.echo(format_health_report(report))
        if not report.healthy:
            raise SystemExit(1)


@health_cmd.command(name="summary")
def summary_cmd():
    """Print a one-line health summary for all stashes."""
    reports = check_all_health()
    if not reports:
        click.echo("No stashes found.")
        return
    total = len(reports)
    healthy = sum(1 for r in reports if r.healthy)
    click.echo(f"{healthy}/{total} stashes healthy.")
    for report in reports:
        if not report.healthy:
            error_count = len(report.errors)
            warn_count = len(report.warnings)
            click.echo(f"  {report.name}: {error_count} error(s), {warn_count} warning(s)")
