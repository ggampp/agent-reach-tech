from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from agent_reach_tech.channels.github import GitHubChannel
from agent_reach_tech.core.subprocess_runner import RunResult


def _run_result(code: int, stdout: str = "", stderr: str = "") -> RunResult:
    return RunResult(command=["gh"], returncode=code, stdout=stdout, stderr=stderr)


@patch("agent_reach_tech.channels.github.which", return_value=None)
def test_probe_without_gh(mock_which):
    status = GitHubChannel().probe()
    assert status.available is False
    assert "not installed" in status.message


@patch("agent_reach_tech.channels.github.run_command")
@patch("agent_reach_tech.channels.github.which", return_value="/bin/gh")
def test_probe_with_gh(mock_which, mock_run):
    mock_run.side_effect = [
        _run_result(0, "gh version 2.0.0\n"),
        _run_result(1, stderr="not logged in"),
    ]
    status = GitHubChannel().probe()
    assert status.available is True
    assert "public repos only" in status.message


@patch("agent_reach_tech.channels.github.run_command")
@patch("agent_reach_tech.channels.github.which", return_value="/bin/gh")
def test_repo_view(mock_which, mock_run):
    payload = {
        "name": "engram",
        "fullName": "Gentleman-Programming/engram",
        "description": "memory",
        "url": "https://github.com/Gentleman-Programming/engram",
        "stargazerCount": 100,
        "forkCount": 10,
        "pushedAt": "2026-01-01",
        "openIssuesCount": 2,
        "licenseInfo": {"spdxId": "MIT"},
        "primaryLanguage": {"name": "Go"},
        "isArchived": False,
        "defaultBranchRef": {"name": "main"},
    }
    mock_run.return_value = _run_result(0, json.dumps(payload))
    data = GitHubChannel().repo_view("Gentleman-Programming/engram")
    assert data["full_name"] == "Gentleman-Programming/engram"
    assert data["stars"] == 100
    assert data["license"] == "MIT"


@patch("agent_reach_tech.channels.github.run_command")
@patch("agent_reach_tech.channels.github.which", return_value="/bin/gh")
def test_search_repos(mock_which, mock_run):
    mock_run.return_value = _run_result(
        0,
        json.dumps(
            [
                {
                    "fullName": "org/repo",
                    "description": "desc",
                    "url": "https://github.com/org/repo",
                    "stargazerCount": 50,
                    "forkCount": 5,
                    "updatedAt": "2026-01-01",
                }
            ]
        ),
    )
    items = GitHubChannel().search_repos("mcp memory", limit=5)
    assert len(items) == 1
    assert items[0]["full_name"] == "org/repo"


@patch.object(GitHubChannel, "http_get_json")
@patch("agent_reach_tech.channels.github.run_command")
@patch("agent_reach_tech.channels.github.which", return_value="/bin/gh")
def test_repo_view_falls_back_to_public_api(mock_which, mock_run, mock_http):
    mock_run.return_value = _run_result(1, stderr="please run: gh auth login")
    mock_http.return_value = {
        "name": "engram",
        "full_name": "Gentleman-Programming/engram",
        "description": "memory",
        "html_url": "https://github.com/Gentleman-Programming/engram",
        "stargazers_count": 100,
        "forks_count": 10,
        "open_issues_count": 1,
        "pushed_at": "2026-01-01",
        "license": {"spdx_id": "MIT"},
        "language": "Go",
        "archived": False,
        "default_branch": "main",
    }
    data = GitHubChannel().repo_view("Gentleman-Programming/engram")
    assert data["source"] == "GitHub REST API (public)"
    assert data["stars"] == 100


@patch("agent_reach_tech.channels.github.which", return_value=None)
def test_repo_view_without_gh_uses_api(mock_which):
    with patch.object(GitHubChannel, "http_get_json") as mock_http:
        mock_http.return_value = {
            "name": "repo",
            "full_name": "a/b",
            "html_url": "https://github.com/a/b",
            "stargazers_count": 1,
            "forks_count": 0,
            "open_issues_count": 0,
        }
        data = GitHubChannel().repo_view("a/b")
        assert data["full_name"] == "a/b"