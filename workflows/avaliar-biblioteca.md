# Workflow: Avaliar biblioteca ou projeto open source

## Entrada

- Nome do pacote/repo (ex: `lodash`, `gentleman-programming/engram`)
- Contexto de uso (ex: "memória para agents", "auth em API Node")

## Passos

### 1. Catálogo local

```bash
agent-reach-tech catalog search NOME
```

Se já catalogado, ler `catalog/` correspondente antes de pesquisar externamente.

### 2. GitHub

```bash
agent-reach-tech github repo OWNER/REPO
agent-reach-tech github search issues "security OR CVE OR vulnerability" --repo OWNER/REPO --limit 10
agent-reach-tech github search repos "OWNER/REPO" --limit 5
```

### 3. Comunidade

```bash
agent-reach-tech hn search "OWNER/REPO OR NOME"
agent-reach-tech lobsters hot   # ver se aparece em discussões recentes
```

### 4. Segurança (se for dependência)

```bash
agent-reach-tech osv npm PACOTE      # ou pypi, go, crates.io
npm audit --json                     # se projeto Node local
```

### 5. Busca semântica

Usar perfil `evaluate_library` em `config/search-profiles.yaml`, substituindo `{name}`.

### 6. Saída esperada

| Critério | Avaliação |
|----------|-----------|
| Manutenção | último commit, frequência de releases |
| Comunidade | stars, issues respondidas, HN/Lobsters |
| Segurança | CVEs conhecidos, tempo de patch |
| Fit | atende o caso de uso? |
| Alternativas | 2–3 opções comparadas |

**Veredito:** adotar | observar | evitar

### 7. Persistência

Se Engram ativo: `mem_save` com type `decision`, topic_key relacionado ao projeto.