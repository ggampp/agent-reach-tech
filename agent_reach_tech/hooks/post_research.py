from __future__ import annotations

import json
from datetime import date
from typing import Any


def format_research_report(
    topic: str,
    *,
    summary: str,
    evidence: list[dict[str, Any]],
    verdict: str,
    reason: str,
    next_step: str = "",
) -> str:
    today = date.today().isoformat()
    lines = [
        f"## Pesquisa: {topic} — {today}",
        "",
        "### Resumo",
        summary.strip() or "_Sem resumo._",
        "",
        "### Evidências",
        "| Fonte | Achado | URL |",
        "|-------|--------|-----|",
    ]
    for item in evidence:
        source = item.get("source", "—")
        finding = (item.get("finding") or item.get("title") or "—").replace("|", "/")
        url = item.get("url", "—")
        lines.append(f"| {source} | {finding} | {url} |")
    if not evidence:
        lines.append("| — | — | — |")
    lines.extend(
        [
            "",
            "### Veredito",
            f"**{verdict}** — {reason.strip() or 'Sem justificativa.'}",
            "",
            "### Próximo passo",
            next_step.strip() or "Revisar evidências e decidir implementação.",
            "",
        ]
    )
    return "\n".join(lines)


def engram_suggestion(
    topic: str,
    verdict: str,
    *,
    summary: str,
    evidence_urls: list[str] | None = None,
) -> dict[str, Any]:
    urls = evidence_urls or []
    return {
        "tool": "mem_save",
        "suggested_payload": {
            "title": f"Research: {topic} → {verdict}",
            "type": "decision",
            "topic_key": topic.lower().replace(" ", "-")[:64],
            "what": summary[:500],
            "why": f"Veredito: {verdict}",
            "where": ", ".join(urls[:5]) or "agent-reach-tech research",
            "learned": "Gerado por agent-reach-tech post-research hook",
        },
        "instruction": "Se Engram ou memoria MCP estiver ativo, chame mem_save com este payload.",
    }


def format_from_json(payload: dict[str, Any]) -> str:
    return format_research_report(
        payload.get("topic", "unknown"),
        summary=payload.get("summary", ""),
        evidence=payload.get("evidence", []),
        verdict=payload.get("verdict", "observar"),
        reason=payload.get("reason", ""),
        next_step=payload.get("next_step", ""),
    )


def full_hook_output(payload: dict[str, Any]) -> str:
    report = format_from_json(payload)
    engram = engram_suggestion(
        payload.get("topic", "unknown"),
        payload.get("verdict", "observar"),
        summary=payload.get("summary", ""),
        evidence_urls=[e.get("url") for e in payload.get("evidence", []) if e.get("url")],
    )
    return report + "\n---\n\n### Engram (opcional)\n```json\n" + json.dumps(engram, indent=2, ensure_ascii=False) + "\n```\n"