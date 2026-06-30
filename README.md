# Agent Reach Tech v1.1

[![CI](https://github.com/ggampp/agent-reach-tech/actions/workflows/ci.yml/badge.svg)](https://github.com/ggampp/agent-reach-tech/actions/workflows/ci.yml)

CLI **standalone** para coding agents pesquisarem tecnologia, desenvolvimento, open source e cibersegurança. Substitui o Agent Reach upstream para o escopo tech.

**Pacote completo:** CLI + skill auto-trigger + servidor MCP (9 tools).

## Instalação (< 10 min)

```powershell
git clone git@github-pessoal:ggampp/agent-reach-tech.git
cd agent-reach-tech
pip install -e ".[mcp]"
agent-reach-tech install --env=auto
agent-reach-tech doctor
```

Ou via pip (sem clonar):

```powershell
pip install "git+https://github.com/ggampp/agent-reach-tech.git#egg=agent-reach-tech[mcp]"
```

Windows helper:

```powershell
.\scripts\install.ps1
```

## Matriz de canais

| Canal | Backend | Obrigatório | Zero-config |
|-------|---------|-------------|-------------|
| github | gh CLI + REST API | Sim | Público sim |
| web | Jina Reader | Sim | Sim |
| youtube | yt-dlp | Sim | Sim |
| rss | feedparser | Sim | Sim |
| hackernews | Algolia API | Sim | Sim |
| lobsters | RSS / JSON | Sim | Sim |
| cve_nvd | NVD API 2.0 | Sim | Sim* |
| osv | OSV.dev | Sim | Sim |
| exa_search | Exa / fallback | Opcional | EXA_API_KEY |
| reddit | pullpush.io | Opcional | Sim |

\* NVD sem key funciona; `NVD_API_KEY` melhora rate limit.

## Comandos

```powershell
# v1.1 — routing e pesquisa orquestrada
agent-reach-tech route "vale a pena usar engram?" --json
agent-reach-tech research oss engram --repo Gentleman-Programming/engram --report
agent-reach-tech research cve CVE-2024-1234 --report
agent-reach-tech research trends --report
agent-reach-tech mcp

# Canais
agent-reach-tech doctor
agent-reach-tech github repo OWNER/REPO
agent-reach-tech web URL
agent-reach-tech youtube info URL
agent-reach-tech rss list
agent-reach-tech rss read URL
agent-reach-tech search --profile evaluate_library --name engram
agent-reach-tech catalog search engram
agent-reach-tech reddit search "cve" --subreddit netsec
```

Ver [docs/MCP-SETUP.md](docs/MCP-SETUP.md) para configurar o servidor MCP no Cursor.

## vs Agent Reach upstream

| | Agent Reach Tech | Upstream |
|--|------------------|----------|
| Foco | Tech/OSS/security | Geral + China social |
| Dependência | Nenhuma | pip upstream |
| Canais | 10 curados | 15+ |
| Catálogo local | Sim | Não |
| Workflows | 4 receitas | SKILL genérico |

## Opcional

```powershell
$env:EXA_API_KEY = "..."   # busca semântica
$env:NVD_API_KEY = "..."    # CVE rate limit
gh auth login               # GitHub privado
```

## Testes

```powershell
pip install -e ".[dev,mcp]"
pytest                  # offline (55+ tests)
pytest -m network       # live APIs
.\scripts\benchmark.ps1
```

## Licença

MIT