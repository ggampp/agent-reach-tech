from __future__ import annotations

import json

from agent_reach_tech.hooks.post_research import (
    engram_suggestion,
    format_from_json,
    format_research_report,
    full_hook_output,
)


def test_format_research_report_structure():
    report = format_research_report(
        "engram",
        summary="Memória persistente para agents.",
        evidence=[{"source": "github", "finding": "4771 stars", "url": "https://github.com/x/engram"}],
        verdict="adotar",
        reason="Projeto maduro.",
        next_step="Instalar e integrar MCP.",
    )
    assert "## Pesquisa: engram" in report
    assert "### Veredito" in report
    assert "**adotar**" in report
    assert "github" in report


def test_engram_suggestion_payload():
    suggestion = engram_suggestion("engram", "adotar", summary="Boa fit para memória local.")
    assert suggestion["tool"] == "mem_save"
    assert suggestion["suggested_payload"]["type"] == "decision"
    assert "engram" in suggestion["suggested_payload"]["topic_key"]


def test_format_from_json():
    payload = {
        "topic": "fastapi",
        "summary": "Framework web Python.",
        "evidence": [],
        "verdict": "observar",
        "reason": "Avaliar stack.",
    }
    report = format_from_json(payload)
    assert "fastapi" in report
    assert "**observar**" in report


def test_full_hook_output_includes_engram():
    payload = {
        "topic": "test-lib",
        "summary": "Test.",
        "evidence": [{"source": "catalog", "finding": "hit", "url": "https://example.com"}],
        "verdict": "observar",
        "reason": "Needs review.",
    }
    output = full_hook_output(payload)
    assert "### Engram (opcional)" in output
    parsed = json.loads(output.split("```json\n")[1].split("\n```")[0])
    assert parsed["tool"] == "mem_save"