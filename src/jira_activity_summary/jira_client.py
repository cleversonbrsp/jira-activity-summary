"""Jira API client for fetching issues and metadata."""

from dataclasses import dataclass, field
from jira import JIRA
from jira.resources import Issue

from .config import Config
from .content import extract_description, summarize_for_executives


@dataclass
class JiraIssue:
    """Simplified representation of a Jira issue for summary generation."""

    key: str
    summary: str
    status: str
    issue_type: str
    priority: str | None
    assignee: str | None
    created: str
    updated: str
    project: str
    labels: list[str] = field(default_factory=list)
    parent_key: str | None = None
    epic_key: str | None = None
    story_points: float | None = None
    description: str = ""
    content_summary: str = ""  # Resumo executivo para diretoria

    @classmethod
    def from_jira_issue(cls, issue: Issue) -> "JiraIssue":
        """Create JiraIssue from Jira REST API Issue object."""
        fields = issue.fields
        status = getattr(fields.status, "name", "Unknown") if fields.status else "Unknown"
        issue_type = getattr(fields.issuetype, "name", "Unknown") if fields.issuetype else "Unknown"
        priority = getattr(fields.priority, "name", None) if fields.priority else None
        assignee = getattr(fields.assignee, "displayName", None) if fields.assignee else None
        project = getattr(fields.project, "key", "Unknown") if fields.project else "Unknown"
        labels = list(fields.labels or [])
        parent_key = None
        if hasattr(fields, "parent") and fields.parent:
            parent_key = getattr(fields.parent, "key", None)
        epic_key = None
        if hasattr(fields, "customfield_10014") and fields.customfield_10014:
            epic_key = fields.customfield_10014
        story_points = None
        if hasattr(fields, "customfield_10016") and fields.customfield_10016 is not None:
            try:
                story_points = float(fields.customfield_10016)
            except (TypeError, ValueError):
                pass
        description_raw = getattr(fields, "description", None)
        description = extract_description(description_raw)
        content_summary = summarize_for_executives(
            description,
            summary_title=fields.summary or "",
            max_length=200,
        )
        return cls(
            key=issue.key,
            summary=fields.summary or "",
            status=status,
            issue_type=issue_type,
            priority=priority,
            assignee=assignee,
            created=fields.created or "",
            updated=fields.updated or "",
            project=project,
            labels=labels,
            parent_key=parent_key,
            epic_key=epic_key,
            story_points=story_points,
            description=description,
            content_summary=content_summary,
        )


class JiraClient:
    """Client for fetching issues from Jira."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._jira = JIRA(
            server=config.jira_url,
            basic_auth=(config.jira_email, config.jira_api_token),
        )

    def fetch_issues(self, max_results: int = 100) -> list[JiraIssue]:
        """Fetch issues matching the configured JQL."""
        jql = self._config.build_jql()
        issues: list[JiraIssue] = []
        start_at = 0
        while True:
            batch = self._jira.search_issues(
                jql_str=jql,
                startAt=start_at,
                maxResults=min(50, max_results - len(issues)),
            )
            for issue in batch:
                issues.append(JiraIssue.from_jira_issue(issue))
            if len(batch) < 50 or len(issues) >= max_results:
                break
            start_at += len(batch)
        return issues
