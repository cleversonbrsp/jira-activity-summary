"""Content extraction and summarization for executive reports."""

import re
from typing import Any


def _adf_to_text(node: Any) -> str:
    """Extract plain text from Atlassian Document Format (ADF) structure."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        text = node.get("text", "")
        if text:
            return str(text)
        parts: list[str] = []
        for child in node.get("content", []):
            parts.append(_adf_to_text(child))
        return " ".join(parts)
    if isinstance(node, list):
        return " ".join(_adf_to_text(item) for item in node)
    return str(node)


def extract_description(raw: Any) -> str:
    """Extract plain text from Jira description (ADF dict or string)."""
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        return _adf_to_text(raw)
    return str(raw)


def _clean_text(text: str) -> str:
    """Remove markdown, extra whitespace, and normalize."""
    if not text:
        return ""
    # Remove markdown links [text](url)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove markdown bold/italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def summarize_for_executives(
    description: str,
    summary_title: str = "",
    max_length: int = 200,
) -> str:
    """
    Create a brief executive summary from task description.
    Suitable for board/directorate (diretoria) - concise, outcome-focused.
    """
    if not description or not description.strip():
        return summary_title if summary_title else ""

    text = _clean_text(description)

    # Prefer first sentence (often the objective/context)
    sentences = re.split(r"[.!?]\s+", text)
    first = (sentences[0] + ".").strip() if sentences else ""

    # If first sentence is too long, truncate at word boundary
    if len(first) > max_length:
        truncated = first[: max_length - 3].rsplit(" ", 1)[0]
        first = (truncated + "...") if truncated else first[:max_length] + "..."

    # If we have nothing meaningful and no description, return empty (avoid duplicating title)
    if not first or len(first) < 10:
        if not text.strip():
            return ""  # No description -> no summary (title already shown)
        return text[:max_length] + ("..." if len(text) > max_length else "")

    return first
