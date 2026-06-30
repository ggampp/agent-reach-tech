from __future__ import annotations

from typing import Any

from .base import Channel, ChannelStatus

HN_ALGOLIA = "https://hn.algolia.com/api/v1"


class HackerNewsChannel(Channel):
    name = "hackernews"
    backend = "Algolia HN API"

    def probe(self) -> ChannelStatus:
        data = self.http_get_json(f"{HN_ALGOLIA}/search?tags=front_page&hitsPerPage=1")
        hits = data.get("hits", [])
        ok = bool(hits)
        return ChannelStatus(
            self.name,
            ok,
            "HN Algolia API reachable" if ok else "No results from HN API",
            self.backend,
        )

    def front_page(self, limit: int = 15) -> list[dict[str, Any]]:
        data = self.http_get_json(f"{HN_ALGOLIA}/search?tags=front_page&hitsPerPage={limit}")
        return [_format_hit(h) for h in data.get("hits", [])]

    def search(self, query: str, limit: int = 15) -> list[dict[str, Any]]:
        from urllib.parse import quote

        q = quote(query)
        data = self.http_get_json(f"{HN_ALGOLIA}/search?query={q}&hitsPerPage={limit}")
        return [_format_hit(h) for h in data.get("hits", [])]


def _format_hit(hit: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": hit.get("title") or hit.get("story_title"),
        "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
        "points": hit.get("points"),
        "author": hit.get("author"),
        "created_at": hit.get("created_at"),
        "num_comments": hit.get("num_comments"),
        "hn_url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
    }