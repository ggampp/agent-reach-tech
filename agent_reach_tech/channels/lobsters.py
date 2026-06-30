from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from .base import Channel, ChannelStatus

LOBSTERS_RSS = "https://lobste.rs/rss"
LOBSTERS_HOT = "https://lobste.rs/hottest.json"


class LobstersChannel(Channel):
    name = "lobsters"
    backend = "lobste.rs RSS + hottest.json"

    def probe(self) -> ChannelStatus:
        self.http_get_text(LOBSTERS_RSS)
        return ChannelStatus(self.name, True, "Lobsters RSS reachable", self.backend)

    def hot(self, limit: int = 15) -> list[dict[str, Any]]:
        try:
            data = self.http_get_json(LOBSTERS_HOT)
            stories = data if isinstance(data, list) else []
            return [
                {
                    "title": s.get("title"),
                    "url": s.get("short_id_url") or s.get("url"),
                    "score": s.get("score"),
                    "comments": s.get("comment_count"),
                    "tags": s.get("tags", []),
                }
                for s in stories[:limit]
            ]
        except Exception:  # noqa: BLE001 — fallback to RSS
            return self._from_rss(limit)

    def _from_rss(self, limit: int) -> list[dict[str, Any]]:
        xml_text = self.http_get_text(LOBSTERS_RSS)
        root = ET.fromstring(xml_text)
        items: list[dict[str, Any]] = []
        for item in root.findall(".//item")[:limit]:
            items.append(
                {
                    "title": _text(item, "title"),
                    "url": _text(item, "link"),
                    "author": _text(item, "dc:creator") or _text(item, "{http://purl.org/dc/elements/1.1/}creator"),
                    "published": _text(item, "pubDate"),
                }
            )
        return items


def _text(elem: ET.Element, tag: str) -> str | None:
    node = elem.find(tag)
    return node.text.strip() if node is not None and node.text else None