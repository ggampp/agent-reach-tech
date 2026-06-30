from __future__ import annotations

from unittest.mock import MagicMock, patch

from agent_reach_tech.channels.rss import RssChannel


@patch("feedparser.parse")
def test_parse_feed(mock_parse):
    entry = MagicMock()
    entry.get = lambda k, d=None: {"title": "T", "link": "http://x", "summary": "S"}.get(k, d)
    feed = MagicMock()
    feed.bozo = False
    feed.entries = [entry]
    feed.feed = {"title": "Feed"}
    mock_parse.return_value = feed
    data = RssChannel().parse("http://example.com/feed.xml")
    assert data["title"] == "Feed"
    assert len(data["entries"]) == 1


def test_list_curated():
    data = RssChannel().list_curated()
    assert "categories" in data
    assert data["total"] > 0