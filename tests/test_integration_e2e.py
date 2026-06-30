from __future__ import annotations

import pytest

from agent_reach_tech import research


@pytest.mark.network
def test_research_oss_engram_e2e():
    result = research.evaluate_oss("engram", repo="Gentleman-Programming/engram")
    assert result["intent"] == "evaluate_oss"
    assert result["topic"] == "engram"
    assert len(result["evidence"]) >= 2
    assert "report" in result
    assert "## Pesquisa: engram" in result["report"]
    assert result["verdict"] in ("adotar", "observar", "evitar")
    github = [e for e in result["evidence"] if e["source"] == "github"]
    assert github and "stars" in github[0]["finding"].lower()