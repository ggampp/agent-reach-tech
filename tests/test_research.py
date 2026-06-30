from __future__ import annotations

from unittest.mock import MagicMock, patch

from agent_reach_tech import research


@patch("agent_reach_tech.research.ExaSearchChannel")
@patch("agent_reach_tech.research.HackerNewsChannel")
@patch("agent_reach_tech.research.GitHubChannel")
@patch("agent_reach_tech.research.catalog.search", return_value=[{"name": "Engram", "url": "https://github.com/x/engram"}])
def test_evaluate_oss_mocked(mock_catalog, mock_gh_cls, mock_hn_cls, mock_exa_cls):
    mock_gh_cls.return_value.repo_view.return_value = {
        "stars": 4771,
        "language": "Go",
        "pushed_at": "2026-01-01",
        "url": "https://github.com/x/engram",
    }
    mock_hn_cls.return_value.search.return_value = [{"title": "Show HN Engram", "url": "https://news.ycombinator.com/x"}]
    mock_exa_cls.return_value.search.return_value = {
        "backend": "fallback",
        "results": [{"title": "Engram review", "url": "https://example.com"}],
    }

    result = research.evaluate_oss("engram", repo="Gentleman-Programming/engram")
    assert result["intent"] == "evaluate_oss"
    assert result["topic"] == "engram"
    assert len(result["evidence"]) >= 2
    assert "report" in result
    assert "## Pesquisa: engram" in result["report"]


@patch("agent_reach_tech.research.RedditChannel")
@patch("agent_reach_tech.research.WebChannel")
@patch("agent_reach_tech.research.CveNvdChannel")
def test_lookup_cve_mocked(mock_cve_cls, mock_web_cls, mock_rd_cls):
    mock_cve_cls.return_value.get_cve.return_value = {
        "url": "https://nvd.nist.gov/vuln/detail/CVE-2024-0001",
        "cvss": {"score": 9.8, "severity": "CRITICAL"},
    }
    mock_web_cls.return_value.read.return_value = {"title": "NVD - CVE-2024-0001"}
    mock_rd_cls.return_value.search.return_value = [{"title": "CVE discussion", "url": "https://reddit.com/x"}]

    result = research.lookup_cve("cve-2024-0001")
    assert result["intent"] == "analyze_cve"
    assert result["topic"] == "CVE-2024-0001"
    assert any(e["source"] == "nvd" for e in result["evidence"])


@patch("agent_reach_tech.research.catalog.search", return_value=[])
@patch("agent_reach_tech.research.HackerNewsChannel")
@patch("agent_reach_tech.research.GitHubChannel")
def test_discover_oss_mocked(mock_gh_cls, mock_hn_cls, _mock_catalog):
    mock_gh_cls.return_value.search_repos.return_value = [
        {"full_name": "org/tool", "url": "https://github.com/org/tool"}
    ]
    mock_hn_cls.return_value.search.return_value = [{"title": "Show HN tool", "url": "https://hn/x"}]

    result = research.discover_oss("task management")
    assert result["intent"] == "discover_oss"
    assert len(result["evidence"]) >= 1


@patch("agent_reach_tech.research.RssChannel")
@patch("agent_reach_tech.research.LobstersChannel")
@patch("agent_reach_tech.research.HackerNewsChannel")
def test_monitor_trends_mocked(mock_hn_cls, mock_lob_cls, mock_rss_cls):
    mock_hn_cls.return_value.front_page.return_value = [{"title": "HN top", "url": "https://hn/1"}]
    mock_lob_cls.return_value.hot.return_value = [{"title": "Lobsters hot", "url": "https://lob/1"}]
    mock_rss_cls.return_value.read_category.return_value = {
        "feeds": [{"name": "krebs", "entries": [{"title": "Security news", "link": "https://kreb/1"}]}]
    }

    result = research.monitor_trends()
    assert result["intent"] == "monitor_trends"
    assert len(result["evidence"]) >= 2