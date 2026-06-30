from __future__ import annotations

import json
from typing import Any

from agent_reach_tech.core.subprocess_runner import run_command, which

from .base import Channel, ChannelStatus

GH_JSON_FIELDS = (
    "name,fullName,description,url,stargazerCount,forkCount,pushedAt,"
    "openIssuesCount,licenseInfo,primaryLanguage,isArchived,defaultBranchRef"
)


class GitHubChannel(Channel):
    name = "github"
    backend = "gh CLI"
    category = "base"

    def _gh_path(self) -> str | None:
        return which("gh")

    def probe(self) -> ChannelStatus:
        gh = self._gh_path()
        if not gh:
            return ChannelStatus(
                self.name,
                False,
                "gh CLI not installed — winget install GitHub.cli",
                self.backend,
                self.category,
            )
        result = run_command([gh, "--version"], timeout=10)
        if not result.success:
            return ChannelStatus(self.name, False, result.stderr.strip() or "gh --version failed", self.backend, self.category)
        version = result.stdout.strip().splitlines()[0] if result.stdout else "gh CLI"
        auth = run_command([gh, "auth", "status"], timeout=10)
        auth_note = "authenticated" if auth.success else "public repos only (run gh auth login for private)"
        return ChannelStatus(self.name, True, f"{version} — {auth_note}", self.backend, self.category)

    def repo_view(self, repo: str) -> dict[str, Any]:
        gh = self._gh_path()
        if gh:
            result = run_command(
                [gh, "repo", "view", repo, "--json", GH_JSON_FIELDS],
                timeout=30,
            )
            if result.success:
                return _format_repo(json.loads(result.stdout))
            if _needs_auth_fallback(result.stderr):
                return self._repo_view_public_api(repo)
            raise RuntimeError(result.stderr.strip() or f"gh repo view failed for {repo}")
        return self._repo_view_public_api(repo)

    def _repo_view_public_api(self, repo: str) -> dict[str, Any]:
        owner, name = _split_repo(repo)
        data = self.http_get_json(f"https://api.github.com/repos/{owner}/{name}")
        if data.get("message") == "Not Found":
            raise RuntimeError(f"Repository not found: {repo}")
        return {
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "description": data.get("description"),
            "url": data.get("html_url"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "open_issues": data.get("open_issues_count"),
            "pushed_at": data.get("pushed_at"),
            "license": (data.get("license") or {}).get("spdx_id"),
            "language": data.get("language"),
            "archived": data.get("archived"),
            "default_branch": data.get("default_branch"),
            "source": "GitHub REST API (public)",
        }

    def search_repos(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        gh = self._require_gh()
        result = run_command(
            [
                gh,
                "search",
                "repos",
                query,
                "--limit",
                str(limit),
                "--json",
                "fullName,description,url,stargazerCount,forkCount,updatedAt",
            ],
            timeout=45,
        )
        if not result.success:
            raise RuntimeError(result.stderr.strip() or "gh search repos failed")
        items = json.loads(result.stdout)
        return [_format_search_repo(item) for item in items]

    def search_issues(self, query: str, limit: int = 10, repo: str | None = None) -> list[dict[str, Any]]:
        gh = self._require_gh()
        q = f"{query} repo:{repo}" if repo else query
        result = run_command(
            [
                gh,
                "search",
                "issues",
                q,
                "--limit",
                str(limit),
                "--json",
                "title,url,repository,state,updatedAt,labels",
            ],
            timeout=45,
        )
        if not result.success:
            raise RuntimeError(result.stderr.strip() or "gh search issues failed")
        items = json.loads(result.stdout)
        return [_format_search_issue(item) for item in items]

    def _require_gh(self) -> str:
        gh = self._gh_path()
        if not gh:
            raise RuntimeError("gh CLI not installed")
        return gh


def _format_repo(data: dict[str, Any]) -> dict[str, Any]:
    license_info = data.get("licenseInfo") or {}
    language = data.get("primaryLanguage") or {}
    default_branch = data.get("defaultBranchRef") or {}
    return {
        "name": data.get("name"),
        "full_name": data.get("fullName"),
        "description": data.get("description"),
        "url": data.get("url"),
        "stars": data.get("stargazerCount"),
        "forks": data.get("forkCount"),
        "open_issues": data.get("openIssuesCount"),
        "pushed_at": data.get("pushedAt"),
        "license": license_info.get("spdxId") or license_info.get("name"),
        "language": language.get("name"),
        "archived": data.get("isArchived"),
        "default_branch": default_branch.get("name"),
    }


def _format_search_repo(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "full_name": item.get("fullName"),
        "description": item.get("description"),
        "url": item.get("url"),
        "stars": item.get("stargazerCount"),
        "forks": item.get("forkCount"),
        "updated_at": item.get("updatedAt"),
    }


def _split_repo(repo: str) -> tuple[str, str]:
    parts = repo.strip().split("/", 1)
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"Invalid repo format (expected OWNER/REPO): {repo}")
    return parts[0], parts[1]


def _needs_auth_fallback(stderr: str) -> bool:
    text = stderr.lower()
    return any(token in text for token in ("auth login", "gh_token", "authentication", "401"))


def _format_search_issue(item: dict[str, Any]) -> dict[str, Any]:
    repository = item.get("repository") or {}
    labels = item.get("labels") or []
    return {
        "title": item.get("title"),
        "url": item.get("url"),
        "state": item.get("state"),
        "updated_at": item.get("updatedAt"),
        "repo": repository.get("nameWithOwner") or repository.get("name"),
        "labels": [label.get("name") for label in labels if label.get("name")],
    }