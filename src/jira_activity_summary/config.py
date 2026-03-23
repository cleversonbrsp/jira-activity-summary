"""Configuration management for Jira Activity Summary."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""

    jira_url: str
    jira_email: str
    jira_api_token: str
    project: str | None = None
    assignee: str | None = None
    jql: str | None = None
    days_back: int = 7
    output_format: str = "markdown"

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate required fields."""
        if not self.jira_url or not self.jira_url.startswith("http"):
            raise ValueError("JIRA_URL must be a valid URL (e.g., https://your-company.atlassian.net)")
        if not self.jira_email or "@" not in self.jira_email:
            raise ValueError("JIRA_EMAIL must be a valid email address")
        if not self.jira_api_token or len(self.jira_api_token.strip()) < 10:
            raise ValueError(
                "JIRA_API_TOKEN is required. Generate one at: "
                "https://id.atlassian.com/manage-profile/security/api-tokens"
            )

    def build_jql(self) -> str:
        """Build JQL query from config. Default: tasks assigned to current user (não as que abriu)."""
        parts: list[str] = []
        if self.jql:
            return self.jql
        # Sempre filtrar por assignee (tarefas atribuídas a mim), nunca por reporter
        assignee_filter = self.assignee or "me"
        if assignee_filter.lower() in ("me", "currentuser", "current"):
            parts.append("assignee = currentUser()")
        else:
            parts.append(f'assignee = "{assignee_filter}"')
        if self.project:
            parts.append(f'project = "{self.project}"')
        date_from = (datetime.now() - timedelta(days=self.days_back)).strftime("%Y-%m-%d")
        parts.append(f'updated >= "{date_from}"')
        return " AND ".join(parts)


def load_config(
    env_file: Path | str | None = None,
    *,
    project: str | None = None,
    assignee: str | None = None,
    jql: str | None = None,
    days_back: int | None = None,
    output_format: str | None = None,
) -> Config:
    """Load configuration from environment and optional overrides."""
    load_dotenv(env_file)

    import os

    config = Config(
        jira_url=os.getenv("JIRA_URL", "").strip(),
        jira_email=os.getenv("JIRA_EMAIL", "").strip(),
        jira_api_token=os.getenv("JIRA_API_TOKEN", "").strip(),
        project=project or os.getenv("JIRA_PROJECT", "").strip() or None,
        assignee=assignee or os.getenv("JIRA_ASSIGNEE", "me").strip() or None,
        jql=jql or os.getenv("JIRA_JQL", "").strip() or None,
        days_back=days_back or int(os.getenv("JIRA_DAYS_BACK", "7")),
        output_format=output_format or os.getenv("JIRA_OUTPUT_FORMAT", "markdown").strip(),
    )
    return config
