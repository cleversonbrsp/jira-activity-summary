"""Tests for summary generation."""

import pytest

from jira_activity_summary.jira_client import JiraIssue
from jira_activity_summary.summary import STATUS_COMPLETED, build_summary


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


def test_build_summary_empty() -> None:
    summary = build_summary([])
    assert summary.total_issues == 0
    assert summary.completed_count == 0
    assert summary.in_progress_count == 0


def test_build_summary_categorizes_statuses() -> None:
    issues = [
        _issue("PROJ-1", "Done"),
        _issue("PROJ-2", "In Progress"),
        _issue("PROJ-3", "To Do"),
        _issue("PROJ-4", "Blocked"),
    ]
    summary = build_summary(issues)
    assert summary.total_issues == 4
    assert summary.completed_count == 1
    assert summary.in_progress_count == 1
    assert summary.todo_count == 1
    assert summary.blocked_count == 1


def test_build_summary_groups_by_status() -> None:
    issues = [_issue("PROJ-1", "Done"), _issue("PROJ-2", "Done")]
    summary = build_summary(issues)
    assert len(summary.by_status["Done"]) == 2
    assert len(summary.completed) == 2


def test_status_completed_includes_common_names() -> None:
    for name in ["done", "closed", "resolved", "complete"]:
        assert name in STATUS_COMPLETED
