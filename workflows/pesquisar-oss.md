# Workflow: Pesquisar projetos open source

## Passos

```bash
agent-reach-tech catalog search "AREA"
agent-reach-tech github search repos "QUERY stars:>500" --limit 20
agent-reach-tech hn search "show hn QUERY"
agent-reach-tech search --profile discover_oss --name "CATEGORIA"
agent-reach-tech rss category opensource --limit 2
```

## Saída

Top 5–10 ranqueados. Para finalistas, rodar `avaliar-biblioteca.md`.

## Catalogar

Adicionar em `manifests/projects.json` se adotar no ecossistema.