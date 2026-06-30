from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from agent_reach_tech.config_loader import load_yaml


@dataclass(frozen=True)
class RouteResult:
    intent: str
    label: str
    workflow: str | None
    commands: list[str]
    matched_keywords: list[str]
    confidence: float
    slash_commands: list[str]


def load_triggers() -> dict[str, Any]:
    return load_yaml("triggers.yaml")


def route_message(message: str) -> RouteResult:
    cfg = load_triggers()
    text = message.lower().strip()
    best_intent = cfg.get("fallback", {}).get("intent", "evaluate_oss")
    best_score = 0
    best_keywords: list[str] = []
    best_spec: dict[str, Any] = {}

    for intent, spec in cfg.get("intents", {}).items():
        score = 0
        matched: list[str] = []
        for kw in spec.get("keywords", []):
            kw_lower = kw.lower()
            if kw_lower.startswith("cve-") and re.search(r"cve-\d{4}-\d+", text):
                score += 10
                matched.append(kw_lower)
            elif kw_lower in text:
                score += len(kw_lower.split()) + 1
                matched.append(kw_lower)
        if score > best_score:
            best_score = score
            best_intent = intent
            best_keywords = matched
            best_spec = spec

    confidence = min(1.0, best_score / 10.0) if best_score else 0.1
    if best_score == 0:
        best_spec = cfg.get("intents", {}).get(best_intent, {})

    return RouteResult(
        intent=best_intent,
        label=best_spec.get("label", best_intent),
        workflow=best_spec.get("workflow"),
        commands=list(best_spec.get("commands", [])),
        matched_keywords=best_keywords,
        confidence=confidence,
        slash_commands=list(cfg.get("slash_commands", [])),
    )