# Changelog

## [1.1.0] — 2026-06-30 — MCP, routing, orchestrated research

### Added
- `config/triggers.yaml` — intent keywords + slash commands (`/research-tech`)
- `agent_reach_tech/triggers.py` — `route_message()` intent router
- `agent_reach_tech/research.py` — `evaluate_oss`, `lookup_cve`, `discover_oss`, `monitor_trends`
- `agent_reach_tech/hooks/post_research.py` — markdown report + Engram `mem_save` suggestion
- `agent_reach_tech/mcp_server.py` — FastMCP server with 9 tools
- CLI: `route`, `triggers`, `research`, `format`, `mcp`
- `scripts/post-research.ps1` — PowerShell report formatter (uses `--file`)
- `config/mcp.json` — MCP client config template
- `docs/MCP-SETUP.md`
- Tests: triggers, post_research, research (mocked), mcp_server, cli v1.1

### Changed
- `pyproject.toml` — optional `[mcp]` extra (`mcp>=1.2.0`)
- `core/installer.py` — suggests `pip install agent-reach-tech[mcp]`
- SKILL.md — v1.1 routing, research commands, MCP tools

## [1.0.0] — 2026-06-30 — Standalone release (Sprints 2–5)

### Added
- **Sprint 2:** `youtube`, `rss` channels + CLI
- **Sprint 3:** `exa_search`, `core/installer.py`, `search` command with profiles
- **Sprint 4:** `reddit` (optional), `catalog search`, standalone doctor, `standalone: true` config
- **Sprint 5:** `docs/ARCHITECTURE.md`, `scripts/benchmark.ps1`, network tests, README matrix
- `feedparser` as core dependency
- `core/skill_install.py`

### Changed
- Doctor: standalone by default, optional channels don't fail probe
- Install: `--env`, `--safe`, `--dry-run`
- All workflows use native CLI only
- Zero references to Agent Reach upstream

## [0.3.0] — Sprint 1: GitHub + Web

## [0.2.0] — Sprint 0: Foundation

## [0.1.0] — Initial tech channels