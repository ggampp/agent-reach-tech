from __future__ import annotations

from unittest.mock import patch

from agent_reach_tech.channels.exa_search import ExaSearchChannel


@patch.dict("os.environ", {}, clear=True)
@patch("agent_reach_tech.channels.exa_search.which", return_value=None)
def test_probe_without_exa(_):
    status = ExaSearchChannel().probe()
    assert status.available is False


@patch("agent_reach_tech.channels.github.GitHubChannel.search_repos", return_value=[{"full_name": "a/b", "url": "u", "description": "d"}])
@patch("agent_reach_tech.channels.hackernews.HackerNewsChannel.search", return_value=[{"title": "t", "url": "u"}])
def test_fallback_search(mock_hn, mock_gh):
    result = ExaSearchChannel().search("engram", limit=5)
    assert result["backend"] == "fallback"
    assert len(result["results"]) >= 1