"""Tests for content extraction and summarization."""

import pytest

from jira_activity_summary.content import (
    extract_description,
    summarize_for_executives,
)


def test_extract_description_string() -> None:
    assert extract_description("Hello world") == "Hello world"


def test_extract_description_none() -> None:
    assert extract_description(None) == ""


def test_extract_description_adf() -> None:
    adf = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Implementar dashboard de métricas."}],
            },
        ],
    }
    assert "Implementar dashboard de métricas" in extract_description(adf)


def test_summarize_for_executives_uses_first_sentence() -> None:
    desc = "Criar nova API de integração com sistemas externos. Detalhes técnicos: REST, auth JWT."
    result = summarize_for_executives(desc)
    assert "API de integração" in result
    assert len(result) <= 203  # max_length + "..."


def test_summarize_for_executives_empty_returns_empty() -> None:
    assert summarize_for_executives("") == ""
    assert summarize_for_executives("   ") == ""


def test_summarize_empty_when_no_useful_description() -> None:
    """Não mostrar 'Situação: X' - não reflete o que foi feito nem próximos passos."""
    result = summarize_for_executives("", summary_title="finops app", status="Fechada")
    assert result == ""


def test_summarize_avoids_duplicating_title() -> None:
    result = summarize_for_executives("finops app", summary_title="finops app")
    assert result == ""  # Same as title, no value added


def test_summarize_extracts_bullets() -> None:
    desc = "- Implementar dashboard\n- Configurar alertas\n- Documentar"
    result = summarize_for_executives(desc)
    assert "dashboard" in result or "alertas" in result

