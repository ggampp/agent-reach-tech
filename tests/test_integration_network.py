from __future__ import annotations

import pytest

from agent_reach_tech.channels.registry import get_channel


@pytest.mark.network
def test_hackernews_front_page_live():
    ch = get_channel("hackernews")
    items = ch.front_page(3)
    assert len(items) >= 1
    assert items[0].get("title")


@pytest.mark.network
def test_catalog_search_live():
    from agent_reach_tech.catalog import search

    hits = search("engram", limit=1)
    assert hits and hits[0]["id"] == "engram"