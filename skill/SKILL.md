---
name: agent-reach-tech
description: >
  Tech/security research CLI for coding agents. Auto-invoke when the user asks to
  research, evaluate, compare, or monitor open source projects, libraries,
  CVEs, vulnerabilities, security advisories, GitHub repos, tech trends,
  Hacker News, or needs structured web research beyond a single URL fetch.
  Triggers: pesquisar, avaliar biblioteca, comparar ferramentas, CVE,
  vulnerabilidade, open source, self-hosted, tendências tech, monitorar feeds,
  vale a pena usar, alternativas a, security audit dependency, /research-tech.
metadata:
  short-description: "Tech/OSS/security research via CLI + MCP"
---

# Agent Reach Tech — Pesquisa Técnica (v1.1)

## Quando usar (auto-trigger)

Use esta skill **proativamente** quando detectar:

| Intenção do usuário | Ação imediata |
|---------------------|---------------|
| Avaliar lib/repo OSS | `research oss` ou fluxo **Avaliar OSS** |
| CVE, vulnerabilidade, exploit | `research cve` ou fluxo **Analisar CVE** |
| Descobrir ferramentas/alternativas | `research discover` ou fluxo **Descobrir OSS** |
| Tendências, o que está em alta | `research trends` ou fluxo **Monitorar** |
| Ler docs/site técnico | `agent-reach-tech web URL` |
| Verificar se já está no catálogo | `agent-reach-tech catalog search TERM` |
| Slash command `/research-tech` | `route` → `research` com report |

**Não usar** para: editar código, fetch de URL trivial já respondida, tarefas sem componente de pesquisa externa.

## Router automático (v1.1)

```bash
agent-reach-tech route "mensagem do usuário" --json
```

Ou, se MCP `agent-reach-tech` estiver ativo: tool `route_intent`.

```
Pedido do usuário
    ├─ menciona CVE / vulnerabilidade / GHSA?     → research cve CVE-ID
    ├─ "vale a pena" / "adotar" / "avaliar" / lib? → research oss NOME
    ├─ "alternativas" / "descobrir" / "melhor X"?  → research discover AREA
    ├─ "tendências" / "briefing"?                  → research trends
    └─ só uma URL / documentação?                  → web URL
```

## Pesquisa orquestrada (preferir em v1.1)

Um comando agrega múltiplos canais e gera relatório markdown + sugestão Engram:

```bash
agent-reach-tech research oss NOME --repo OWNER/REPO --report
agent-reach-tech research cve CVE-2024-1234 --report
agent-reach-tech research discover "task management" --report
agent-reach-tech research trends --report
```

Sem `--report`: JSON completo com campo `report` embutido.

## Regras de execução

1. **Sempre executar CLI ou MCP** — não simular pesquisa
2. **Route primeiro** se intenção ambígua: `agent-reach-tech route "..." --json`
3. **Catálogo primeiro** — `catalog search` antes de pesquisa externa
4. **Mínimo 2 fontes** — ex: GitHub + HN, ou CVE + NVD web
5. **Citar URLs e data** em toda conclusão
6. **Veredito explícito** — adotar | observar | evitar (com justificativa)
7. **Persistir** — se Engram/memoria MCP ativo: `mem_save` com decisões relevantes

## Comandos CLI

```bash
# v1.1 — routing e pesquisa
agent-reach-tech route "vale a pena usar engram?" --json
agent-reach-tech triggers
agent-reach-tech research oss engram --repo Gentleman-Programming/engram --report
agent-reach-tech research cve CVE-2024-1234 --report
agent-reach-tech research discover "memory agents" --report
agent-reach-tech research trends --report
agent-reach-tech format --file resultado.json

# Canais (v1.0)
agent-reach-tech catalog search TERM
agent-reach-tech github repo OWNER/REPO
agent-reach-tech github search repos|issues "QUERY"
agent-reach-tech web URL
agent-reach-tech youtube info URL
agent-reach-tech rss category cybersecurity|opensource|development
agent-reach-tech hn search "QUERY"
agent-reach-tech hn front-page
agent-reach-tech lobsters hot
agent-reach-tech cve CVE-YYYY-NNNN
agent-reach-tech osv npm|pypi PACKAGE
agent-reach-tech search --profile PROFILE --name NAME
agent-reach-tech reddit search "QUERY" --subreddit netsec
agent-reach-tech doctor
agent-reach-tech mcp   # servidor MCP stdio
```

Perfis de busca: `evaluate_library`, `cve_research`, `discover_oss`, `agent_tooling`

## MCP Server (v1.1)

Instalar: `pip install agent-reach-tech[mcp]`

Configurar em `.cursor/mcp.json` ou `config/mcp.json`:

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

Tools disponíveis:

| Tool | Uso |
|------|-----|
| `route_intent` | Classificar mensagem do usuário |
| `catalog_search` | Buscar no catálogo local |
| `evaluate_repo` | Avaliação OSS completa |
| `lookup_cve` | Análise de CVE |
| `research_oss` | Descobrir projetos por categoria |
| `monitor_trends` | Briefing HN + Lobsters + RSS |
| `read_web` | Ler URL via Jina |
| `github_repo` | Metadados de repositório |
| `format_research_report` | JSON → markdown + Engram |

## Slash commands

- `/research-tech` — pesquisa tech estruturada (route → research → report)
- `/agent-reach-tech` — alias
- `/pesquisa-tech` — alias PT

## Fluxo: Avaliar OSS

**Rápido (v1.1):**
```bash
agent-reach-tech research oss NOME --repo OWNER/REPO --report
```

**Manual (granular):**
1. `agent-reach-tech catalog search NOME`
2. `agent-reach-tech github repo OWNER/REPO`
3. `agent-reach-tech hn search "REPO"`
4. `agent-reach-tech osv npm|pypi PACOTE` (se dependência)
5. `agent-reach-tech search --profile evaluate_library --name NOME`
6. Entregar tabela + veredito → `mem_save` se Engram disponível

## Fluxo: Analisar CVE

**Rápido:** `agent-reach-tech research cve CVE-ID --report`

**Manual:**
1. `agent-reach-tech cve CVE-ID`
2. `agent-reach-tech web https://nvd.nist.gov/vuln/detail/CVE-ID`
3. `agent-reach-tech reddit search CVE-ID --subreddit netsec`

## Fluxo: Descobrir OSS

**Rápido:** `agent-reach-tech research discover "AREA" --report`

## Fluxo: Monitorar

**Rápido:** `agent-reach-tech research trends --report`

## Formato de resposta (obrigatório)

Gerado automaticamente por `research --report` ou `format`:

```markdown
## Pesquisa: [tópico] — [data]

### Resumo
[2-3 frases]

### Evidências
| Fonte | Achado | URL |
|-------|--------|-----|

### Veredito
**adotar | observar | evitar** — [motivo]

### Próximo passo
[ação concreta]
```

PowerShell helper: `.\scripts\post-research.ps1 -Topic X -Verdict observar`

## Configuração

- `EXA_API_KEY` — busca semântica (fallback: gh + hn)
- `NVD_API_KEY` — rate limit CVE
- `gh auth login` — repos privados
- `pip install agent-reach-tech[mcp]` — servidor MCP

## Workflows detalhados

`agent-reach-tech/workflows/avaliar-biblioteca.md` e demais em `workflows/`