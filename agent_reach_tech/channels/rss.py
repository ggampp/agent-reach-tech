from __future__ import annotations

from datetime import datetime
from typing import Any

from agent_reach_tech.config_loader import load_yaml

from .base import Channel, ChannelStatus


class RssChannel(Channel):
    name = "rss"
    backend = "feedparser"
    category = "base"

    def probe(self) -> ChannelStatus:
        try:
            import feedparser  # noqa: PLC0415
        except ImportError:
            return ChannelStatus(
                self.name,
                False,
                "feedparser not installed — pip install feedparser",
                self.backend,
                self.category,
            )
        version = getattr(feedparser, "__version__", "unknown")
        return ChannelStatus(self.name, True, f"feedparser {version}", self.backend, self.category)

    def parse(self, url: str, limit: int = 15) -> dict[str, Any]:
        import feedparser  # noqa: PLC0415

        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            raise RuntimeError(f"Failed to parse feed: {feed.bozo_exception}")
        entries = []
        for entry in feed.entries[:limit]:
            entries.append(
                {
                    "title": entry.get("title"),
                    "link": entry.get("link"),
                    "published": entry.get("published") or entry.get("updated"),
                    "summary": _trim(entry.get("summary", ""), 300),
                    "author": entry.get("author"),
                }
            )
        return {
            "url": url,
            "title": feed.feed.get("title"),
            "entry_count": len(feed.entries),
            "entries": entries,
        }

    def list_curated(self) -> dict[str, Any]:
        data = load_yaml("feeds.yaml")
        feeds = data.get("feeds", {})
        summary: dict[str, Any] = {}
        for category, items in feeds.items():
            summary[category] = [
                {"name": item.get("name"), "url": item.get("url"), "tags": item.get("tags", [])}
                for item in items
            ]
        return {"categories": list(summary.keys()), "feeds": summary, "total": sum(len(v) for v in summary.values())}

    def read_category(self, category: str, limit: int = 5) -> dict[str, Any]:
        data = load_yaml("feeds.yaml")
        feeds = data.get("feeds", {}).get(category, [])
        if not feeds:
            raise ValueError(f"Unknown feed category: {category}")
        results = []
        for item in feeds[:limit]:
            try:
                parsed = self.parse(item["url"], limit=3)
                results.append({"name": item.get("name"), "url": item["url"], "entries": parsed["entries"]})
            except Exception as e:  # noqa: BLE001
                results.append({"name": item.get("name"), "url": item["url"], "error": str(e)})
        return {"category": category, "feeds": results}


def _trim(text: str, max_len: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= max_len else text[: max_len - 3] + "..."