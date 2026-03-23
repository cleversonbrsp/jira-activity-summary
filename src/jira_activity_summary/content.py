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


def _normalize_for_compare(s: str) -> str:
    """Normalize string for similarity comparison."""
    return re.sub(r"\s+", " ", s.lower().strip())[:50]


def _first_n_lines(text: str, n: int = 5, max_chars: int = 500) -> str:
    """Return first n non-empty lines joined with space. Cap at max_chars."""
    lines = [line.strip() for line in text.split("\n") if line.strip()][:n]
    result = " ".join(lines)
    if len(result) > max_chars:
        result = result[: max_chars - 3].rsplit(" ", 1)[0] + "..."
    return result


def summarize_for_executives(
    description: str,
    summary_title: str = "",
    status: str = "",
    max_lines: int = 5,
) -> str:
    """
    Create a brief executive summary from task content.
    Usa as primeiras N linhas (padrão: 5) do comentário ou descrição.
    """
    text = _clean_text(description or "").strip()
    title_norm = _normalize_for_compare(summary_title) if summary_title else ""

    if not text or len(text) < 10:
        return ""

    result = _first_n_lines(text, max_lines)

    # Evitar repetir o título
    if _normalize_for_compare(result) == title_norm:
        return ""

    return result
