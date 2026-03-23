"""Tests for config and JQL building."""

import os

import pytest

from jira_activity_summary.config import Config


def test_build_jql_always_includes_assignee_by_default() -> None:
    """Default JQL must filter by assignee (tarefas atribuídas), never reporter."""
    config = Config(
        jira_url="https://test.atlassian.net",
        jira_email="u@t.com",
        jira_api_token="x" * 20,
        assignee=None,
        project=None,
    )
    jql = config.build_jql()
    assert "assignee = currentUser()" in jql
    assert "reporter" not in jql


def test_build_jql_custom_assignee() -> None:
    config = Config(
        jira_url="https://test.atlassian.net",
        jira_email="u@t.com",
        jira_api_token="x" * 20,
        assignee="joao@empresa.com",
    )
    jql = config.build_jql()
    assert "assignee = \"joao@empresa.com\"" in jql


def test_build_jql_custom_overrides_default() -> None:
    config = Config(
        jira_url="https://test.atlassian.net",
        jira_email="u@t.com",
        jira_api_token="x" * 20,
        jql="project = X ORDER BY created DESC",
    )
    assert config.build_jql() == "project = X ORDER BY created DESC"
