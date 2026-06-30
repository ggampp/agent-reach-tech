# MCP Setup — Agent Reach Tech v1.1

## Instalação

```powershell
pip install -e ".[mcp]"
# ou
pip install agent-reach-tech[mcp]
```

Verificar:

```powershell
agent-reach-tech doctor
agent-reach-tech route "avaliar engram" --json
```

## Cursor

Copie ou mescle em `.cursor/mcp.json` na raiz do workspace:

```json
{
  "mcpServers": {
    "agent-reach-tech": {
      "command": "agent-reach-tech",
      "args": ["mcp"],
      "env": {}
    }
  }
}
```

Reinicie o Cursor após salvar. O servidor usa transporte stdio.

Template em `agent-reach-tech/config/mcp.json`.

## Antigravity / Gemini Agent

Arquivo: `~/.gemini/config/mcp_config.json`

```json
{
  "mcpServers": {
    "agent-reach-tech": {
      "command": "agent-reach-tech",
      "args": ["mcp"],
      "env": {}
    }
  }
}
```

Reinicie o Antigravity após salvar. Conexões remotas (`serverUrl` + `headers`) também são suportadas pelo IDE.

## Claude Desktop / outros clientes MCP

```json
{
  "mcpServers": {
    "agent-reach-tech": {
      "command": "agent-reach-tech",
      "args": ["mcp"]
    }
  }
}
```

Certifique-se de que `agent-reach-tech` está no PATH (após `pip install`).

## Tools expostas

| Tool | Descrição |
|------|-----------|
| `route_intent(message)` | Roteia intenção via `triggers.yaml` |
| `catalog_search(term, limit)` | Catálogo local `manifests/projects.json` |
| `evaluate_repo(name, repo?, ecosystem?, package?)` | Avaliação OSS multi-canal |
| `lookup_cve(cve_id)` | NVD + web + Reddit |
| `research_oss(category)` | Descoberta por categoria |
| `monitor_trends()` | HN + Lobsters + RSS security |
| `read_web(url)` | Jina Reader |
| `github_repo(repo)` | Metadados GitHub |
| `format_research_report(payload_json)` | Markdown + sugestão Engram |

## Fluxo recomendado para agents

1. `route_intent` — se intenção não for óbvia
2. Tool de pesquisa adequada (`evaluate_repo`, `lookup_cve`, etc.)
3. `format_research_report` — se precisar reformatar JSON manual
4. `mem_save` via Engram — se MCP memoria estiver ativo

## Instalação em múltiplos agents

```powershell
cd agent-reach-tech
.\scripts\install-mcp.ps1
# ou
python -m agent_reach_tech.core.mcp_install --project C:\claude_projects\projetos_exemplo
```

| Agent | Config | Suportado |
|-------|--------|-----------|
| Cursor | `~/.cursor/mcp.json` + `.cursor/mcp.json` (projeto) | Sim |
| Claude Code | `~/.claude/mcp.json` | Sim |
| Grok | `~/.grok/config.toml` + `.grok/config.toml` (projeto) | Sim |
| Codex | `~/.codex/config.toml` | Sim |
| Antigravity / Gemini Agent | `~/.gemini/config/mcp_config.json` | Sim |
| Windsurf | Sem `mcp.json` padrão detectado | Skill only |

Após instalar, reinicie o agent/IDE. Validar:

```powershell
grok mcp doctor agent-reach-tech
python -c "import asyncio; from mcp import ClientSession, StdioServerParameters; from mcp.client.stdio import stdio_client; ..."
```

## Troubleshooting

| Problema | Solução |
|----------|---------|
| `MCP SDK not installed` | `pip install agent-reach-tech[mcp]` |
| Comando não encontrado | `pip install -e .` e reiniciar terminal |
| GitHub rate limit | `gh auth login` |
| Busca semântica vazia | Definir `EXA_API_KEY` ou usar fallback automático |