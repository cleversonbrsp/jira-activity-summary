"""Command-line interface for Jira Activity Summary."""

from pathlib import Path

import click

from .config import load_config
from .jira_client import JiraClient
from .report import (
    format_console,
    format_english_markdown,
    format_english_txt,
    format_markdown,
    format_txt,
)
from .summary import build_summary


@click.command()
@click.option(
    "--env",
    "env_file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to .env file (default: .env in cwd)",
)
@click.option(
    "--project", "-p",
    type=str,
    default=None,
    help="Jira project key (e.g., PROJ)",
)
@click.option(
    "--assignee", "-a",
    type=str,
    default=None,
    help="Assignee (e.g., me, user@email.com)",
)
@click.option(
    "--jql", "-q",
    type=str,
    default=None,
    help="Custom JQL query (overrides project/assignee/days)",
)
@click.option(
    "--days",
    "days_back",
    type=int,
    default=None,
    help="Number of days to look back (default: 7)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "txt", "english", "console"]),
    default="txt",
    help="Output format: txt (plain text), markdown, english, console (default: txt)",
)
@click.option(
    "--output", "-o",
    "output_file",
    type=click.Path(path_type=Path),
    default=None,
    help="Write report to file instead of stdout",
)
@click.option(
    "--max-results",
    type=int,
    default=100,
    help="Maximum number of issues to fetch (default: 100)",
)
@click.option(
    "--lang",
    type=click.Choice(["pt", "en"]),
    default="pt",
    help="Report language: pt (Portuguese) or en (English)",
)
@click.option(
    "--include-subtasks/--no-subtasks",
    "include_subtasks",
    default=False,
    help="Incluir sub-tasks (tarefas filhas). Padrão: excluir, mostrar só tasks principais.",
)
def main(
    env_file: Path | None,
    project: str | None,
    assignee: str | None,
    jql: str | None,
    days_back: int | None,
    output_format: str,
    output_file: Path | None,
    max_results: int,
    lang: str,
    include_subtasks: bool,
) -> None:
    """Fetch Jira tasks and generate activity summaries for leadership."""
    try:
        config = load_config(
            env_file=env_file,
            project=project,
            assignee=assignee,
            jql=jql,
            days_back=days_back,
            output_format=output_format,
        )
    except ValueError as e:
        raise click.ClickException(str(e))

    click.echo("Connecting to Jira...", err=True)
    client = JiraClient(config)
    click.echo(f"Fetching issues (JQL: {config.build_jql()[:80]}...)", err=True)
    issues = client.fetch_issues(max_results=max_results)

    if not include_subtasks:
        before = len(issues)
        issues = [i for i in issues if not i.is_subtask]
        click.echo(f"Found {len(issues)} issues ({before - len(issues)} sub-tasks excluídas).", err=True)
    else:
        click.echo(f"Found {len(issues)} issues.", err=True)

    summary = build_summary(issues)

    if output_format == "console":
        report = format_console(summary)
    elif output_format == "txt":
        report = format_english_txt(summary) if lang == "en" else format_txt(summary)
    elif lang == "en" or output_format == "english":
        report = format_english_markdown(summary)
    else:
        report = format_markdown(summary)

    if output_file:
        output_file.write_text(report, encoding="utf-8")
        click.echo(f"Report written to {output_file}", err=True)
    else:
        click.echo(report)


if __name__ == "__main__":
    main()
