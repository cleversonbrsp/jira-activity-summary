"""Report formatting for activity summaries."""

from .jira_client import JiraIssue
from .summary import ActivitySummary


def _format_issue_list(
    issues: list[JiraIssue],
    show_priority: bool = False,
    empty_msg: str = "_No items_",
    include_content_summary: bool = True,
    summary_label: str = "Resumo",
) -> str:
    """Format issue list, optionally including executive content summary."""
    lines = []
    for i in sorted(issues, key=lambda x: x.key):
        priority = f" [{i.priority}]" if show_priority and i.priority else ""
        lines.append(f"- **{i.key}**{priority}: {i.summary}")
        if include_content_summary and i.content_summary:
            lines.append(f"  - _{summary_label}:_ {i.content_summary}")
    return "\n".join(lines) if lines else empty_msg


def format_markdown(summary: ActivitySummary) -> str:
    """Format activity summary as Markdown for leadership."""
    sections = [
        f"# Resumo de Atividade — {summary.generated_at}",
        "",
        "## Visão geral",
        "",
        f"| Métrica | Quantidade |",
        f"|---------|------------|",
        f"| Total de itens | {summary.total_issues} |",
        f"| Concluídos | {summary.completed_count} |",
        f"| Em progresso | {summary.in_progress_count} |",
        f"| Pendentes | {summary.todo_count} |",
        f"| Bloqueados | {summary.blocked_count} |",
        "",
    ]

    if summary.completed:
        sections.extend([
            "## Concluídos",
            "",
            _format_issue_list(summary.completed, show_priority=False, summary_label="Resumo"),
            "",
        ])

    if summary.in_progress:
        sections.extend([
            "## Em progresso",
            "",
            _format_issue_list(summary.in_progress, show_priority=True, summary_label="Resumo"),
            "",
        ])

    if summary.blocked:
        sections.extend([
            "## Bloqueados",
            "",
            _format_issue_list(summary.blocked, show_priority=True, summary_label="Resumo"),
            "",
        ])

    if summary.todo:
        sections.extend([
            "## Pendentes (próximos)",
            "",
            _format_issue_list(summary.todo[:15], show_priority=True, summary_label="Resumo"),
            "",
        ])
        if len(summary.todo) > 15:
            sections.append(f"_... e mais {len(summary.todo) - 15} itens_")
            sections.append("")

    return "\n".join(sections)


def format_english_markdown(summary: ActivitySummary) -> str:
    """Format activity summary as Markdown (English) for leadership."""
    sections = [
        f"# Activity Summary — {summary.generated_at}",
        "",
        "## Overview",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total items | {summary.total_issues} |",
        f"| Completed | {summary.completed_count} |",
        f"| In progress | {summary.in_progress_count} |",
        f"| Pending | {summary.todo_count} |",
        f"| Blocked | {summary.blocked_count} |",
        "",
    ]

    if summary.completed:
        sections.extend([
            "## Completed",
            "",
            _format_issue_list(summary.completed, show_priority=False, summary_label="Summary"),
            "",
        ])

    if summary.in_progress:
        sections.extend([
            "## In progress",
            "",
            _format_issue_list(summary.in_progress, show_priority=True, summary_label="Summary"),
            "",
        ])

    if summary.blocked:
        sections.extend([
            "## Blocked",
            "",
            _format_issue_list(summary.blocked, show_priority=True, summary_label="Summary"),
            "",
        ])

    if summary.todo:
        sections.extend([
            "## Pending (up next)",
            "",
            _format_issue_list(summary.todo[:15], show_priority=True, summary_label="Summary"),
            "",
        ])
        if len(summary.todo) > 15:
            sections.append(f"_... and {len(summary.todo) - 15} more items_")
            sections.append("")

    return "\n".join(sections)


def _format_issue_list_txt(
    issues: list[JiraIssue],
    show_priority: bool = False,
    summary_label: str = "Resumo",
) -> list[str]:
    """Format issue list for plain text output."""
    lines = []
    for i in sorted(issues, key=lambda x: x.key):
        priority = f" [{i.priority}]" if show_priority and i.priority else ""
        lines.append(f"  - {i.key}{priority}: {i.summary}")
        if i.content_summary:
            lines.append(f"    {summary_label}: {i.content_summary}")
    return lines


def format_txt(summary: ActivitySummary) -> str:
    """Format activity summary as plain text (.txt) for leadership."""
    sections = [
        f"RESUMO DE ATIVIDADE — {summary.generated_at}",
        "",
        "VISÃO GERAL",
        "-" * 40,
        f"Total de itens:   {summary.total_issues}",
        f"Concluídos:       {summary.completed_count}",
        f"Em progresso:     {summary.in_progress_count}",
        f"Pendentes:        {summary.todo_count}",
        f"Bloqueados:       {summary.blocked_count}",
        "",
    ]

    if summary.completed:
        sections.extend(["CONCLUÍDOS", "-" * 40] + _format_issue_list_txt(summary.completed, summary_label="Resumo") + [""])

    if summary.in_progress:
        sections.extend(["EM PROGRESSO", "-" * 40] + _format_issue_list_txt(summary.in_progress, show_priority=True, summary_label="Resumo") + [""])

    if summary.blocked:
        sections.extend(["BLOQUEADOS", "-" * 40] + _format_issue_list_txt(summary.blocked, show_priority=True, summary_label="Resumo") + [""])

    if summary.todo:
        sections.extend(["PENDENTES (próximos)", "-" * 40] + _format_issue_list_txt(summary.todo[:15], show_priority=True, summary_label="Resumo") + [""])
        if len(summary.todo) > 15:
            sections.append(f"... e mais {len(summary.todo) - 15} itens")
            sections.append("")

    return "\n".join(sections)


def format_english_txt(summary: ActivitySummary) -> str:
    """Format activity summary as plain text (.txt) in English."""
    sections = [
        f"ACTIVITY SUMMARY — {summary.generated_at}",
        "",
        "OVERVIEW",
        "-" * 40,
        f"Total items:   {summary.total_issues}",
        f"Completed:     {summary.completed_count}",
        f"In progress:   {summary.in_progress_count}",
        f"Pending:       {summary.todo_count}",
        f"Blocked:       {summary.blocked_count}",
        "",
    ]

    if summary.completed:
        sections.extend(["COMPLETED", "-" * 40] + _format_issue_list_txt(summary.completed, summary_label="Summary") + [""])

    if summary.in_progress:
        sections.extend(["IN PROGRESS", "-" * 40] + _format_issue_list_txt(summary.in_progress, show_priority=True, summary_label="Summary") + [""])

    if summary.blocked:
        sections.extend(["BLOCKED", "-" * 40] + _format_issue_list_txt(summary.blocked, show_priority=True, summary_label="Summary") + [""])

    if summary.todo:
        sections.extend(["PENDING (up next)", "-" * 40] + _format_issue_list_txt(summary.todo[:15], show_priority=True, summary_label="Summary") + [""])
        if len(summary.todo) > 15:
            sections.append(f"... and {len(summary.todo) - 15} more items")
            sections.append("")

    return "\n".join(sections)


def format_console(summary: ActivitySummary) -> str:
    """Format activity summary for console output (compact)."""
    lines = [
        f"Activity Summary — {summary.generated_at}",
        f"  Total: {summary.total_issues} | Done: {summary.completed_count} | "
        f"In Progress: {summary.in_progress_count} | Pending: {summary.todo_count} | "
        f"Blocked: {summary.blocked_count}",
    ]
    if summary.in_progress:
        lines.append("  In progress:")
        for i in summary.in_progress[:10]:
            lines.append(f"    • {i.key}: {i.summary[:50]}{'...' if len(i.summary) > 50 else ''}")
    return "\n".join(lines)
