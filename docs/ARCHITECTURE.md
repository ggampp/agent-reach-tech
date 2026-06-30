# Architecture — Agent Reach Tech v1.1

## Overview

```
CLI (agent_reach_tech/cli.py)
    ├── doctor.py          → channel probes + deps
    ├── triggers.py        → intent routing (triggers.yaml)
    ├── research.py        → orchestrated multi-channel research
    ├── mcp_server.py      → FastMCP tools (optional [mcp] extra)
    ├── hooks/post_research.py → markdown report + Engram hint
    ├── core/installer.py  → install orchestration
    ├── core/skill_install.py
    ├── catalog.py         → local manifests/projects.json
    └── channels/
            registry.py    → channel registry
            base.py        → HTTP/subprocess helpers
            github.py, web.py, youtube.py, rss.py
            exa_search.py, reddit.py (optional)
            hackernews.py, lobsters.py, cve_nvd.py, osv.py
```

## v1.1 research flow

```
user message
    → triggers.route_message()
    → research.evaluate_oss | lookup_cve | discover_oss | monitor_trends
    → hooks.post_research.full_hook_output()
    → markdown report + mem_save suggestion
```

MCP exposes the same stack as tools for agent clients.

## Channel contract

Every channel implements:
- `name`, `backend`, `category`, `optional`
- `probe() -> ChannelStatus`
- `safe_probe()` — never raises

Optional channels (`exa_search`, `reddit`) do not fail `doctor`.

## Search degradation

```
search request
    ├── EXA_API_KEY set → Exa REST API
    └── fallback → GitHub search + Hacker News search
```

## GitHub degradation

```
repo_view
    ├── gh repo view (authenticated)
    └── GitHub REST API (public repos)
```

## Config

| File | Purpose |
|------|---------|
| `config/channels.yaml` | Standalone mode, enabled channels |
| `config/feeds.yaml` | Curated RSS |
| `config/search-profiles.yaml` | Query templates |
| `config/sources.yaml` | Domain → source mapping |
| `config/triggers.yaml` | Intent keywords + slash commands |
| `config/mcp.json` | MCP client config template |

## Tests

- Offline: `pytest` (default, mocks)
- Online: `pytest -m network`