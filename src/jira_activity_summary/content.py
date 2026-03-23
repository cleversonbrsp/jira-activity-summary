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


def _extract_bullets(text: str, max_items: int = 2) -> str:
    """Extract first bullet/numbered items from text."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    items = []
    for line in lines:
        m = re.match(r"^[-*•]\s+(.+)", line) or re.match(r"^\d+[.)]\s+(.+)", line)
        if m:
            items.append(_clean_text(m.group(1)))
        elif items:
            break
    if items:
        return " | ".join(items[:max_items])[:150]
    # ADF pode vir sem newlines: "Item 1. Item 2. Item 3"
    parts = re.split(r"\s*[•\-]\s+|\s*\d+[.)]\s+", text)
    if len(parts) > 1:
        meaningful = [p.strip() for p in parts[1:3] if len(p.strip()) > 5]
        if meaningful:
            return " | ".join(meaningful)[:150]
    return ""


def summarize_for_executives(
    description: str,
    summary_title: str = "",
    status: str = "",
    max_length: int = 150,
) -> str:
    """
    Create a brief executive summary from task content.
    Reads description and summarizes in few words (em que pé está / o que é).
    """
    text = _clean_text(description or "").strip()
    title_norm = _normalize_for_compare(summary_title) if summary_title else ""

    # 1. If we have meaningful description, extract essence
    if len(text) > 15:
        # Prefer bullet points (often the key deliverables)
        bullets = _extract_bullets(text)
        if bullets and _normalize_for_compare(bullets) != title_norm:
            return bullets[:max_length] + ("..." if len(bullets) > max_length else "")

        # Otherwise first sentence
        sentences = re.split(r"[.!?]\s+", text)
        first = (sentences[0] + ".").strip() if sentences else ""

        # Skip if same as title or generic
        if first and len(first) > 15 and _normalize_for_compare(first) != title_norm:
            if len(first) > max_length:
                first = first[: max_length - 3].rsplit(" ", 1)[0] + "..."
            return first

        # First 2 sentences if first is too short
        if len(first) < 20 and len(sentences) > 1:
            combined = first + " " + (sentences[1] + ".").strip()
            if _normalize_for_compare(combined) != title_norm:
                return combined[:max_length] + ("..." if len(combined) > max_length else "")

    # Sem descrição útil: não mostrar nada (evitar "Situação: Em Progresso" redundante)
    return ""
