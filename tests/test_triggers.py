from __future__ import annotations

from agent_reach_tech.triggers import load_triggers, route_message


def test_load_triggers_has_intents():
    cfg = load_triggers()
    assert "intents" in cfg
    assert "evaluate_oss" in cfg["intents"]
    assert "/research-tech" in cfg.get("slash_commands", [])


def test_route_cve_intent():
    result = route_message("analisar CVE-2024-1234 no projeto")
    assert result.intent == "analyze_cve"
    assert result.confidence > 0
    assert "cve-" in result.matched_keywords or "cve" in result.matched_keywords


def test_route_evaluate_oss_intent():
    result = route_message("vale a pena adotar esta biblioteca?")
    assert result.intent == "evaluate_oss"
    assert result.workflow == "avaliar-biblioteca.md"


def test_route_discover_oss_intent():
    result = route_message("alternativas self-hosted para notion")
    assert result.intent == "discover_oss"


def test_route_monitor_trends_intent():
    result = route_message("briefing de tendências security news")
    assert result.intent == "monitor_trends"


def test_route_fallback_when_unclear():
    result = route_message("xyz random query 12345")
    assert result.intent == "evaluate_oss"
    assert result.confidence <= 0.2


def test_route_slash_commands_present():
    result = route_message("/research-tech engram")
    assert "/research-tech" in result.slash_commands