from __future__ import annotations

from datetime import date
from typing import Any

from agent_reach_tech import catalog
from agent_reach_tech.channels.cve_nvd import CveNvdChannel
from agent_reach_tech.channels.exa_search import ExaSearchChannel
from agent_reach_tech.channels.github import GitHubChannel
from agent_reach_tech.channels.hackernews import HackerNewsChannel
from agent_reach_tech.channels.lobsters import LobstersChannel
from agent_reach_tech.channels.osv import OsvChannel
from agent_reach_tech.channels.reddit import RedditChannel
from agent_reach_tech.channels.rss import RssChannel
from agent_reach_tech.channels.web import WebChannel
from agent_reach_tech.hooks.post_research import full_hook_output


def _evidence(source: str, finding: str, url: str = "") -> dict[str, str]:
    return {"source": source, "finding": finding, "url": url}


def evaluate_oss(
    name: str,
    *,
    repo: str | None = None,
    ecosystem: str | None = None,
    package: str | None = None,
) -> dict[str, Any]:
    evidence: list[dict[str, str]] = []
    errors: list[str] = []

    try:
        hits = catalog.search(name, limit=3)
        if hits:
            evidence.append(_evidence("catalog", hits[0].get("name", name), hits[0].get("url", "")))
    except Exception as e:  # noqa: BLE001
        errors.append(f"catalog: {e}")

    if repo:
        try:
            data = GitHubChannel().repo_view(repo)
            evidence.append(
                _evidence(
                    "github",
                    f"{data.get('stars')} stars, {data.get('language')}, pushed {data.get('pushed_at')}",
                    data.get("url", ""),
                )
            )
        except Exception as e:  # noqa: BLE001
            errors.append(f"github: {e}")

    try:
        for item in HackerNewsChannel().search(name, limit=3):
            evidence.append(_evidence("hackernews", item.get("title", ""), item.get("url", "")))
    except Exception as e:  # noqa: BLE001
        errors.append(f"hn: {e}")

    if ecosystem and package:
        try:
            osv = OsvChannel().query_package(ecosystem, package)
            evidence.append(_evidence("osv", f"{osv.get('count')} vulnerabilities", "https://osv.dev"))
        except Exception as e:  # noqa: BLE001
            errors.append(f"osv: {e}")

    try:
        search = ExaSearchChannel().search(name, profile="evaluate_library", name=name, limit=5)
        for r in search.get("results", [])[:3]:
            evidence.append(_evidence(search.get("backend", "search"), r.get("title", ""), r.get("url", "")))
    except Exception as e:  # noqa: BLE001
        errors.append(f"search: {e}")

    stars = next((e["finding"] for e in evidence if e["source"] == "github"), "")
    verdict = "observar"
    reason = "Dados insuficientes para decisão forte."
    if "stars" in stars and any(c.isdigit() for c in stars):
        verdict = "adotar" if "1000" in stars or "4771" in stars or "500" in stars else "observar"
        reason = "Métricas GitHub e comunidade consideradas."

    payload = {
        "topic": name,
        "intent": "evaluate_oss",
        "date": date.today().isoformat(),
        "summary": f"Avaliação de {name}" + (f" ({repo})" if repo else ""),
        "evidence": evidence,
        "verdict": verdict,
        "reason": reason,
        "next_step": "Validar fit com o projeto atual antes de adotar.",
        "errors": errors,
    }
    payload["report"] = full_hook_output(payload)
    return payload


def lookup_cve(cve_id: str) -> dict[str, Any]:
    evidence: list[dict[str, str]] = []
    errors: list[str] = []
    cve_id = cve_id.upper().strip()

    try:
        data = CveNvdChannel().get_cve(cve_id)
        if data:
            cvss = data.get("cvss") or {}
            evidence.append(
                _evidence(
                    "nvd",
                    f"CVSS {cvss.get('score')} {cvss.get('severity')}",
                    data.get("url", ""),
                )
            )
    except Exception as e:  # noqa: BLE001
        errors.append(f"nvd: {e}")

    try:
        page = WebChannel().read(f"https://nvd.nist.gov/vuln/detail/{cve_id}")
        evidence.append(_evidence("web", page.get("title") or "NVD page", f"https://nvd.nist.gov/vuln/detail/{cve_id}"))
    except Exception as e:  # noqa: BLE001
        errors.append(f"web: {e}")

    try:
        for item in RedditChannel().search(cve_id, limit=3, subreddit="netsec"):
            evidence.append(_evidence("reddit", item.get("title", ""), item.get("url", "")))
    except Exception as e:  # noqa: BLE001
        errors.append(f"reddit: {e}")

    payload = {
        "topic": cve_id,
        "intent": "analyze_cve",
        "date": date.today().isoformat(),
        "summary": f"Análise de {cve_id}",
        "evidence": evidence,
        "verdict": "observar",
        "reason": "Avaliar impacto nas dependências e patches disponíveis.",
        "next_step": "Checar versões afetadas no projeto e aplicar patch.",
        "errors": errors,
    }
    payload["report"] = full_hook_output(payload)
    return payload


def discover_oss(category: str) -> dict[str, Any]:
    evidence: list[dict[str, str]] = []
    errors: list[str] = []

    try:
        for item in GitHubChannel().search_repos(f"{category} stars:>500", limit=8):
            evidence.append(_evidence("github", item.get("full_name", ""), item.get("url", "")))
    except Exception as e:  # noqa: BLE001
        errors.append(f"github: {e}")

    try:
        for item in HackerNewsChannel().search(f"show hn {category}", limit=5):
            evidence.append(_evidence("hackernews", item.get("title", ""), item.get("url", "")))
    except Exception as e:  # noqa: BLE001
        errors.append(f"hn: {e}")

    try:
        hits = catalog.search(category, limit=5)
        for h in hits:
            evidence.append(_evidence("catalog", h.get("name", ""), h.get("url", "")))
    except Exception as e:  # noqa: BLE001
        errors.append(f"catalog: {e}")

    payload = {
        "topic": category,
        "intent": "discover_oss",
        "date": date.today().isoformat(),
        "summary": f"Descoberta OSS em: {category}",
        "evidence": evidence,
        "verdict": "observar",
        "reason": "Lista candidata — avaliar cada finalista individualmente.",
        "next_step": "Rodar evaluate_oss nos top 3.",
        "errors": errors,
    }
    payload["report"] = full_hook_output(payload)
    return payload


def monitor_trends() -> dict[str, Any]:
    evidence: list[dict[str, str]] = []
    errors: list[str] = []

    try:
        for item in HackerNewsChannel().front_page(5):
            evidence.append(_evidence("hackernews", item.get("title", ""), item.get("url", "")))
    except Exception as e:  # noqa: BLE001
        errors.append(f"hn: {e}")

    try:
        for item in LobstersChannel().hot(5):
            evidence.append(_evidence("lobsters", item.get("title", ""), item.get("url", "")))
    except Exception as e:  # noqa: BLE001
        errors.append(f"lobsters: {e}")

    try:
        rss = RssChannel().read_category("cybersecurity", limit=2)
        for feed in rss.get("feeds", []):
            for entry in feed.get("entries", [])[:2]:
                evidence.append(_evidence(f"rss:{feed.get('name')}", entry.get("title", ""), entry.get("link", "")))
    except Exception as e:  # noqa: BLE001
        errors.append(f"rss: {e}")

    payload = {
        "topic": "tech/security trends",
        "intent": "monitor_trends",
        "date": date.today().isoformat(),
        "summary": "Briefing de tendências tech e security",
        "evidence": evidence,
        "verdict": "observar",
        "reason": "Monitoramento — sem decisão de adoção.",
        "next_step": "Filtrar itens relevantes ao catálogo e projetos ativos.",
        "errors": errors,
    }
    payload["report"] = full_hook_output(payload)
    return payload