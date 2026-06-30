from __future__ import annotations

import os
from typing import Any

from agent_reach_tech.config_loader import load_yaml
from agent_reach_tech.core.subprocess_runner import which

from .base import Channel, ChannelStatus
from .hackernews import HackerNewsChannel

EXA_API = "https://api.exa.ai/search"


class ExaSearchChannel(Channel):
    name = "exa_search"
    backend = "Exa API / fallback"
    category = "base"
    optional = True

    def probe(self) -> ChannelStatus:
        key = os.environ.get("EXA_API_KEY", "").strip()
        mcporter = which("mcporter")
        if key:
            return ChannelStatus(
                self.name,
                True,
                "EXA_API_KEY set — Exa REST API",
                "Exa REST",
                self.category,
            )
        if mcporter:
            return ChannelStatus(
                self.name,
                True,
                f"mcporter found ({mcporter}) — configure Exa MCP",
                "mcporter",
                self.category,
            )
        return ChannelStatus(
            self.name,
            False,
            "Set EXA_API_KEY or install mcporter — fallback: gh/hn search available",
            self.backend,
            self.category,
        )

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        profile: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        queries = _build_queries(query, profile=profile, name=name)
        primary = queries[0] if queries else query

        key = os.environ.get("EXA_API_KEY", "").strip()
        if key:
            try:
                results = self._exa_api(primary, key, limit)
                return {
                    "query": primary,
                    "backend": "exa",
                    "profile": profile,
                    "results": results,
                }
            except Exception as e:  # noqa: BLE001
                fallback = self._fallback_search(primary, limit)
                fallback["exa_error"] = str(e)
                return fallback

        return self._fallback_search(primary, limit, profile=profile)

    def _exa_api(self, query: str, api_key: str, limit: int) -> list[dict[str, Any]]:
        payload = {
            "query": query,
            "numResults": limit,
            "useAutoprompt": True,
            "type": "auto",
        }
        data = self.http_post_json(
            EXA_API,
            payload,
            headers={"x-api-key": api_key},
        )
        return [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "score": r.get("score"),
                "published": r.get("publishedDate"),
                "snippet": (r.get("text") or "")[:300],
            }
            for r in data.get("results", [])
        ]

    def _fallback_search(self, query: str, limit: int, profile: str | None = None) -> dict[str, Any]:
        from .github import GitHubChannel

        results: dict[str, Any] = {
            "query": query,
            "backend": "fallback",
            "profile": profile,
            "results": [],
            "sources": [],
        }
        try:
            gh_items = GitHubChannel().search_repos(query, min(limit, 5))
            results["sources"].append("github")
            results["results"].extend(
                [{"title": i["full_name"], "url": i["url"], "snippet": i.get("description"), "source": "github"} for i in gh_items]
            )
        except Exception:  # noqa: BLE001
            pass
        try:
            hn_items = HackerNewsChannel().search(query, min(limit, 5))
            results["sources"].append("hackernews")
            results["results"].extend(
                [{"title": i["title"], "url": i["url"], "snippet": None, "source": "hackernews"} for i in hn_items]
            )
        except Exception:  # noqa: BLE001
            pass
        return results


def _build_queries(query: str, profile: str | None = None, name: str | None = None) -> list[str]:
    if not profile:
        return [query]
    profiles = load_yaml("search-profiles.yaml").get("profiles", {})
    spec = profiles.get(profile, {})
    templates = spec.get("queries", [])
    if not templates:
        return [query]
    token = name or query
    return [t.replace("{name}", token).replace("{cve_id}", token).replace("{category}", token).replace("{product}", token).replace("{technology}", token) for t in templates]