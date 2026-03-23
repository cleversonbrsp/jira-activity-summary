"""Activity summary generation from Jira issues."""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from .jira_client import JiraIssue


@dataclass
class ActivitySummary:
    """Structured activity summary for leadership."""

    total_issues: int = 0
    by_status: dict[str, list[JiraIssue]] = field(default_factory=lambda: defaultdict(list))
    by_type: dict[str, list[JiraIssue]] = field(default_factory=lambda: defaultdict(list))
    by_priority: dict[str, list[JiraIssue]] = field(default_factory=lambda: defaultdict(list))
    by_project: dict[str, list[JiraIssue]] = field(default_factory=lambda: defaultdict(list))
    completed: list[JiraIssue] = field(default_factory=list)
    in_progress: list[JiraIssue] = field(default_factory=list)
    todo: list[JiraIssue] = field(default_factory=list)
    blocked: list[JiraIssue] = field(default_factory=list)
    generated_at: str = ""

    def __post_init__(self) -> None:
        if not self.generated_at:
            self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    @property
    def completed_count(self) -> int:
        return len(self.completed)

    @property
    def in_progress_count(self) -> int:
        return len(self.in_progress)

    @property
    def todo_count(self) -> int:
        return len(self.todo)

    @property
    def blocked_count(self) -> int:
        return len(self.blocked)


# Common status names that indicate completion, progress, todo, or blocked
STATUS_COMPLETED = frozenset(
    {"done", "closed", "resolved", "complete", "finished", "released"}
)
STATUS_IN_PROGRESS = frozenset(
    {"in progress", "in review", "code review", "testing", "qa", "in development"}
)
STATUS_BLOCKED = frozenset(
    {"blocked", "on hold", "waiting", "blocked by dependency"}
)
STATUS_TODO = frozenset(
    {"to do", "open", "backlog", "ready", "ready for dev", "planned"}
)


def _normalize_status(s: str) -> str:
    return (s or "").strip().lower()


def _categorize_status(status: str) -> str:
    """Return one of: completed, in_progress, todo, blocked."""
    n = _normalize_status(status)
    if n in STATUS_COMPLETED:
        return "completed"
    if n in STATUS_IN_PROGRESS:
        return "in_progress"
    if n in STATUS_BLOCKED:
        return "blocked"
    return "todo"


def build_summary(issues: list[JiraIssue]) -> ActivitySummary:
    """Build an ActivitySummary from a list of Jira issues."""
    summary = ActivitySummary()
    summary.total_issues = len(issues)

    for issue in issues:
        status_norm = _normalize_status(issue.status)
        summary.by_status[issue.status].append(issue)
        summary.by_type[issue.issue_type].append(issue)
        if issue.priority:
            summary.by_priority[issue.priority].append(issue)
        summary.by_project[issue.project].append(issue)

        cat = _categorize_status(issue.status)
        if cat == "completed":
            summary.completed.append(issue)
        elif cat == "in_progress":
            summary.in_progress.append(issue)
        elif cat == "blocked":
            summary.blocked.append(issue)
        else:
            summary.todo.append(issue)

    return summary
