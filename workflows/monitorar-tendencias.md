# Workflow: Monitorar tendências tech/security

## Frequência

- Diário: HN, Lobsters, RSS cybersecurity
- Semanal: GitHub search por tópicos do catálogo

## Passos

```bash
agent-reach-tech hn front-page
agent-reach-tech lobsters hot
agent-reach-tech rss category cybersecurity --limit 3
agent-reach-tech rss category opensource --limit 3
agent-reach-tech github search repos "created:>YYYY-MM-DD stars:>100" --limit 15
```

## Filtro de relevância

Manter itens sobre: coding agents, MCP, devtools, OSS self-hosted, CVEs relevantes.

## Saída

Briefing com seções Segurança / Open Source / Ação sugerida.

## Persistência

`mem_save` type `observation` para follow-ups.