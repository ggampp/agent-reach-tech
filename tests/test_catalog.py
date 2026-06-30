from __future__ import annotations

from unittest.mock import patch

from agent_reach_tech import catalog


SAMPLE = {
    "projects": [
        {"id": "engram", "name": "Engram", "summary": "memory", "tags": ["mcp"], "use_cases": []},
        {"id": "mira", "name": "Mira", "summary": "review", "tags": [], "use_cases": []},
    ]
}


@patch.object(catalog, "load_catalog", return_value=SAMPLE)
def test_search_by_id(_):
    hits = catalog.search("engram")
    assert hits[0]["id"] == "engram"


@patch.object(catalog, "load_catalog", return_value=SAMPLE)
def test_search_by_tag(_):
    hits = catalog.search("mcp")
    assert any(h["id"] == "engram" for h in hits)