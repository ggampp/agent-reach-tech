from __future__ import annotations

import json
import sys
from typing import Any


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def run_mcp() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "MCP SDK not installed. Run: pip install agent-reach-tech[mcp]",
            file=sys.stderr,
        )
        return 1

    from agent_reach_tech import catalog, research
    from agent_reach_tech.channels.github import GitHubChannel
    from agent_reach_tech.channels.web import WebChannel
    from agent_reach_tech.hooks.post_research import format_from_json, full_hook_output
    from agent_reach_tech.triggers import route_message

    mcp = FastMCP(
        "agent-reach-tech",
        instructions=(
            "Tech/security research tools. Use route_intent first when unsure. "
            "After research, use format_research_report for standardized output."
        ),
    )

    @mcp.tool()
    def route_intent(message: str) -> str:
        """Route user message to research intent (evaluate_oss, analyze_cve, discover_oss, monitor_trends, read_docs)."""
        r = route_message(message)
        return _json(
            {
                "intent": r.intent,
                "label": r.label,
                "workflow": r.workflow,
                "commands": r.commands,
                "matched_keywords": r.matched_keywords,
                "confidence": r.confidence,
                "slash_commands": r.slash_commands,
            }
        )

    @mcp.tool()
    def catalog_search(term: str, limit: int = 5) -> str:
        """Search local open source catalog (manifests/projects.json)."""
        return _json(catalog.search(term, limit=limit))

    @mcp.tool()
    def evaluate_repo(name: str, repo: str = "", ecosystem: str = "", package: str = "") -> str:
        """Full OSS evaluation: catalog + GitHub + HN + optional OSV + search. Returns report markdown."""
        return _json(
            research.evaluate_oss(
                name,
                repo=repo or None,
                ecosystem=ecosystem or None,
                package=package or None,
            )
        )

    @mcp.tool()
    def lookup_cve(cve_id: str) -> str:
        """Analyze CVE via NVD, web, Reddit. Returns structured report."""
        return _json(research.lookup_cve(cve_id))

    @mcp.tool()
    def research_oss(category: str) -> str:
        """Discover open source projects in a category."""
        return _json(research.discover_oss(category))

    @mcp.tool()
    def monitor_trends() -> str:
        """HN + Lobsters + RSS cybersecurity briefing."""
        return _json(research.monitor_trends())

    @mcp.tool()
    def read_web(url: str) -> str:
        """Read URL as markdown via Jina Reader."""
        return _json(WebChannel().read(url))

    @mcp.tool()
    def github_repo(repo: str) -> str:
        """Get GitHub repository metadata (OWNER/REPO)."""
        return _json(GitHubChannel().repo_view(repo))

    @mcp.tool()
    def format_research_report(payload_json: str) -> str:
        """Format research JSON into markdown report with Engram mem_save suggestion."""
        payload = json.loads(payload_json)
        return full_hook_output(payload) if "topic" in payload else format_from_json(payload)

    mcp.run()
    return 0