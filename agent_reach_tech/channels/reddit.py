from __future__ import annotations

from typing import Any
from urllib.parse import quote

from agent_reach_tech.core.subprocess_runner import run_command, which

from .base import Channel, ChannelStatus

PULLPUSH_API = "https://api.pullpush.io/reddit/search/submission/"


class RedditChannel(Channel):
    name = "reddit"
    backend = "pullpush.io / rdt-cli"
    category = "base"
    optional = True

    DEFAULT_SUBREDDITS = ["programming", "netsec", "opensource", "cybersecurity"]

    def probe(self) -> ChannelStatus:
        rdt = which("rdt") or which("rdt-cli")
        try:
            data = self.http_get_json(f"{PULLPUSH_API}?q=test&size=1")
            if data.get("data"):
                backend = "pullpush.io"
                if rdt:
                    backend += f" + rdt ({rdt})"
                return ChannelStatus(self.name, True, f"Reddit search via {backend}", self.backend, self.category)
        except Exception:  # noqa: BLE001
            pass
        if rdt:
            return ChannelStatus(self.name, True, f"rdt-cli available ({rdt})", "rdt-cli", self.category)
        return ChannelStatus(
            self.name,
            False,
            "Reddit unavailable — install rdt-cli or check network",
            self.backend,
            self.category,
        )

    def search(self, query: str, limit: int = 10, subreddit: str | None = None) -> list[dict[str, Any]]:
        params = f"q={quote(query)}&size={limit}"
        if subreddit:
            params += f"&subreddit={quote(subreddit)}"
        data = self.http_get_json(f"{PULLPUSH_API}?{params}")
        posts = data.get("data", [])
        return [
            {
                "title": p.get("title"),
                "url": p.get("url") or f"https://reddit.com{p.get('permalink', '')}",
                "subreddit": p.get("subreddit"),
                "score": p.get("score"),
                "num_comments": p.get("num_comments"),
                "created_utc": p.get("created_utc"),
                "selftext": (p.get("selftext") or "")[:300],
            }
            for p in posts
        ]