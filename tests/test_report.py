"""Tests for report formatting."""

from jira_activity_summary.jira_client import JiraIssue
from jira_activity_summary.report import format_markdown
from jira_activity_summary.summary import build_summary


def _issue(key: str, status: str, summary: str = "Task") -> JiraIssue:
    return JiraIssue(
        key=key,
        summary=summary,
        status=status,
        issue_type="Task",
        priority="High",
        assignee="user",
        created="2024-01-01",
        updated="2024-01-02",
        project="PROJ",
    )


def test_format_markdown_includes_overview() -> None:
    issues = [_issue("PROJ-1", "Done")]
    summary = build_summary(issues)
    report = format_markdown(summary)
    assert "Visão geral" in report
    assert "PROJ-1" in report
    assert "Concluídos" in report
    assert "Total de itens" in report
