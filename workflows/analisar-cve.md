# Workflow: Analisar CVE

## Passos

```bash
agent-reach-tech cve CVE-YYYY-NNNN
agent-reach-tech web https://nvd.nist.gov/vuln/detail/CVE-YYYY-NNNN
agent-reach-tech github search issues "CVE-YYYY-NNNN"
agent-reach-tech reddit search "CVE-YYYY-NNNN" --subreddit netsec
agent-reach-tech search --profile cve_research --name CVE-YYYY-NNNN
agent-reach-tech osv npm|pypi PACOTE   # se aplicável
```

## Saída

Severidade, produtos afetados, patch, exploit público, ação recomendada.

## Persistência

`mem_save` se impacta dependências do projeto.